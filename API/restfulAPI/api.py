from flask import Flask,request
from flask_restful import Resource, Api
import requests,re
#scrapping data from the web
from bs4 import BeautifulSoup
from selenium import webdriver

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
jobs = []

#the twilio job page url
twilioUrl = 'https://www.twilio.com/company/jobs'
#get the hidden data from twilio
driver = webdriver.PhantomJS(executable_path='D:\\web\\reactJS\\codingChanllenge\\API\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
driver.get(twilioUrl)
sourceTwilio = driver.page_source
soupTwilio = BeautifulSoup(sourceTwilio,'html.parser')

#from airbnb job pages
airbnbUrl='https://www.airbnb.com/careers/departments'
sourceAirbnb = requests.get(airbnbUrl).text
soupAirbnb = BeautifulSoup(sourceAirbnb,'html.parser')

#list of airbnb category
categories = []
OpenPositions= []

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

#scraping and store from Twillio
for category in soupTwilio.find_all('div',class_='collapse'):
    # categoryprint(category['id'])
    for engineering in category.find_all('li'):
        position = engineering.a.text #position
        company = 'Twilio' #company name
        location = engineering.a.span.text#locaion
        link = engineering.a['href']#link
        id = re.findall('\\d+',link)    #id
        OpenPositions.append(OpenPosition(id,position,location,link,company))

#define to retrieve the whole lists
class jobList(Resource):
    def get(self):
        return {'jobs' : jobs}

    #add in all positions into the lists
    def post(self):
        #data = request.get_json()
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
