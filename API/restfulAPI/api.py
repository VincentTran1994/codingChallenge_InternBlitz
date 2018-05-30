from flask import Flask
from flask_restful import Resource, Api
import requests,re,json
#scrapping data from the web
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)

#list of jobs for both companies
OpenPositions= []

#from airbnb job pages
airbnbUrl='https://www.airbnb.com/careers/departments'
sourceAirbnb = requests.get(airbnbUrl).text
soupAirbnb = BeautifulSoup(sourceAirbnb,'html.parser')

#store lists of link in the categories
for categoryLink in soupAirbnb.find_all('a',class_='jobs-card link-reset'):
    #getting all catergory urls
    catergoryUrl = 'https://www.airbnb.com' + categoryLink['href']
    tempSource = requests.get(catergoryUrl).text
    soupPositions = BeautifulSoup(tempSource,'html.parser')
    if soupPositions.tbody:
        for soupPosition in soupPositions.find_all('tr'):
            if soupPosition.td:
                #get position url
                link = 'https://www.airbnb.com' + soupPosition.td.a['href']
                job = {
                    'position' : soupPosition.td.a.text,   #job position
                    'location' : soupPosition.select_one('td:nth-of-type(2)').a.text ,  #location
                    'link' : link, #job link
                    'id' : re.findall('\\d+',link),   #id
                    'company' : 'Airbnb'  #company
                }
                #append into the lists
                OpenPositions.append(job)

# from the yext Api
yextUrl = 'https://api.greenhouse.io/v1/boards/yext/embed/departments'
sourceYext = json.loads((requests.get(yextUrl)).text)['departments']
#from the yext Api
for jobs in sourceYext:
    if jobs['jobs']:
        for job in jobs['jobs']:
            job = {
                'id' : job['id'],#id
                'position' : job['title'], #postion
                'location' : job['location']['name'],#location
                'link' : job['absolute_url'], #link
                'company' : 'Yext'
            }
            #append into the lists
            OpenPositions.append(job)

#from the twilio API
twilioUrl = 'https://api.greenhouse.io/v1/boards/twilio/embed/jobs?&content=true&_=1527657664356'
sourceTwilio = json.loads((requests.get(twilioUrl)).text)['jobs']

#store data from Twillio API
for jobTwilio in sourceTwilio:
    jobTwilio = {
        'link' : sourceTwilio[0]['absolute_url'],
        'location' : sourceTwilio[0]['location']['name'], #location
        'id' : sourceTwilio[0]['id'],#id
        'position' : sourceTwilio[0]['title'], #position
        'company' : 'Twilio'
    }
    #append into the lists
    OpenPositions.append(jobTwilio)

#define to retrieve the whole lists
class jobList(Resource):
    def get(self):
        return {'jobs' : OpenPositions}
    #testing api
    def post(self):
        #data = request.get_json()
        return OpenPositions,201

#getting a single job position with ID
class Job(Resource):
    #get one item from the lists
    def get(self,id):
        # for job in jobs:
        #     if job['id'][0] == id:
        #        return job
        #similar to the for loop ablove
        OpenPosition = next(filter(lambda x: x['id'][0] == id, OpenPositions), None)
        return {'job': OpenPosition},200 if OpenPosition else 404

#api.add_resource(Job, '/airbnb/job/<string:name>')
api.add_resource(Job, '/job/<string:id>') #http://127.0.0.1:5000/airbnb/job/<string:name
api.add_resource(jobList, '/')

app.run(port=4000, debug=True)
