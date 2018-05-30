from flask import Flask,render_template,url_for
import requests,json

app = Flask(__name__)

#getting the whold data from the final API http://127.0.0.1:4000
#this API no need authentication or key
dataSource = json.loads((requests.get('http://127.0.0.1:4000')).text)['jobs']

#store data in order
airbnbJobs = []
twilioJobs = []
yextJobs = []
for data in dataSource:
    if data['company'] == 'Airbnb':
        airbnbJobs.append(data)
    if  data['company'] == 'Twilio':
        twilioJobs.append(data)
    if  data['company'] == 'Yext':
        yextJobs.append(data)


#home route
@app.route('/')
def home():
    return render_template('homepage.html')

#airbnb page
@app.route('/airbnb')
def aribnb():
    #render the render_template and data
    return render_template('airbnb.html',airbnbJobs = airbnbJobs)

#twilio page
@app.route('/twilio')
def twilio():
    #render the render_template and data
    return render_template('twilio.html',twilioJobs = twilioJobs)

#Yext page
@app.route('/yext')
def yext():
    #render the render_template and data
    return render_template('Yext.html',yextJobs = yextJobs)


app.run(port=5000,debug=True)
