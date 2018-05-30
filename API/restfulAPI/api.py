from flask import Flask,request
from flask_restful import Resource, Api
import requests,re,json
#scrapping data from the web
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)

class OpenPosition():
    def __init__(self,id, position, location, link,company):
        self.id = id
        self.position = position
        self.location = location
        self.link = link
        self.company = company

#list of jobs for both companies
OpenPositions= []

#from airbnb job pages
airbnbUrl='https://www.airbnb.com/careers/departments'
sourceAirbnb = requests.get(airbnbUrl).text
soupAirbnb = BeautifulSoup(sourceAirbnb,'html.parser')

#list of airbnb category
categories = []
#store lists of link in the categories
for categoryLink in soupAirbnb.find_all('a',class_='jobs-card link-reset'):
    #getting all links
    categories.append('https://www.airbnb.com' + categoryLink['href'])
#scarping data from every single link of categories
for categoryLink in categories:
    #print(categoryLink)
    tempSource = requests.get(categoryLink).text
    soupPositions = BeautifulSoup(tempSource,'html.parser')
    if soupPositions.tbody:
        for soupPosition in soupPositions.find_all('tr'):
            if soupPosition.td:
                position = soupPosition.td.a.text   #job position
                location = soupPosition.select_one('td:nth-of-type(2)').a.text  #location
                link = 'https://www.airbnb.com' + soupPosition.td.a['href'] #job link
                id = re.findall('\\d+',link)    #id
                company = 'Airbnb'  #company
                OpenPositions.append(OpenPosition(id,position,location,link,company))

# from the yext Api
yextUrl = 'https://api.greenhouse.io/v1/boards/yext/embed/departments'
sourceYext = json.loads((requests.get(yextUrl)).text)['departments']
#from the yext Api
for jobs in sourceYext:
    if jobs['jobs']:
        for job in jobs['jobs']:
            id = job['id']#id
            position = job['title'] #postion
            location = job['location']['name']#location
            link = job['absolute_url'] #link
            company = 'Yext'
            OpenPositions.append(OpenPosition(id,position,location,link,company))

#from the twilio API
twilioUrl = 'https://api.greenhouse.io/v1/boards/twilio/embed/jobs?&content=true&_=1527657664356'
sourceTwilio = json.loads((requests.get(twilioUrl)).text)['jobs']

#scraping and store from Twillio
for jobTwilio in sourceTwilio:
    link = sourceTwilio[0]['absolute_url']
    location = sourceTwilio[0]['location']['name'] #location
    id = sourceTwilio[0]['id'] #id
    position = sourceTwilio[0]['title'] #position
    company = 'Twilio'
    OpenPositions.append(OpenPosition(id,position,location,link,company))

#api render purpose
jobs = []
#add in all positions into the lists
for OpenPosition in OpenPositions:
    job = {
        # 'OpenPositions': OpenPositions,
        'id' : OpenPosition.id,
        'position' : OpenPosition.position ,
        'location' : OpenPosition.location ,
        'link' : OpenPosition.link,
        'company': OpenPosition.company
    }
    jobs.append(job)



#define to retrieve the whole lists
class jobList(Resource):
    def get(self):
        return {'jobs' : jobs}
    #testing api
    def post(self):
        #data = request.get_json()
        return jobs,201

#getting a single job position with ID
class Job(Resource):
    #get one item from the lists
    def get(self,id):
        # for job in jobs:
        #     if job['id'][0] == id:
        #        return job
        #similar to the for loop ablove
        job = next(filter(lambda x: x['id'][0] == id, jobs), None)
        return {'job': job},200 if job else 404


#api.add_resource(Job, '/airbnb/job/<string:name>')
api.add_resource(Job, '/job/<string:id>') #http://127.0.0.1:5000/airbnb/job/<string:name
api.add_resource(jobList, '/')


app.run(port=4000, debug=True)
