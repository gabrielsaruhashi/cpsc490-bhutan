from flask import Flask, jsonify
from rq import Queue
from rq.job import Job
from rq_scheduler import Scheduler
import operator

from worker import conn
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
import sys 
import os
from flask_sqlalchemy import SQLAlchemy
import googlemaps


app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
q = Queue('queue', connection=conn)
scheduler = Scheduler(queue=q, connection=conn)

gmaps = googlemaps.Client(key=os.environ['GMAPS_KEY'])

from models import *

def generateURL(start_date, end_date):
        print("Generating url for the week of " + str(start_date) + " to " +str(end_date))
        BASE_URL = 'http://www.ktracker.bt/report/trip?r_uin%5B%5D=__all_sub&r_date_time_type=1&r_date='
        return BASE_URL + \
            str(start_date) + '+00%3A00+-+' + str(end_date) + \
            '+00%3A00&r_judge=1&r_page_size=100&r_drtn=2&_k=&r_search='

def dailyScrape():
    # initialize driver
    driver = webdriver.Chrome('./chromedriver')

    # login and get access credentials
    driver.get('http://www.ktracker.bt/')
    driver.find_element_by_id("loginAccount").send_keys(os.environ['KTRACKER_LOGIN'])
    driver.find_element_by_id("loginPassword").send_keys(os.environ['KTRACKER_PASSWORD'])
    driver.find_element_by_xpath("//button[@type='submit']").click()

    # pick the date ranges
    START_DATE = datetime.now() - timedelta(1)
    WINDOW = 1
    
    # define main data frame that will store 
    df = pd.DataFrame()
    index = len(df.index)

    url = generateURL(START_DATE.date(), (START_DATE + timedelta(days=WINDOW)).date())
    driver.get(url)
    pages_remaining = True

    errors = []
    while pages_remaining:

        table = driver.find_element_by_id('report')

        for row in table.find_elements_by_xpath('.//tr'):
            ambulance_id = [td.text for td in row.find_elements_by_xpath(".//td[1]")]
            addr = [td.text for td in row.find_elements_by_xpath(".//td[3]")]
            timestamp_from = [td.text for td in row.find_elements_by_xpath(".//td[4]")]
            start_addr = [td.text for td in row.find_elements_by_xpath(".//td[5]")]
            timestamp_to = [td.text for td in row.find_elements_by_xpath(".//td[6]")]
            end_addr = [td.text for td in row.find_elements_by_xpath(".//td[7]")]
            trip_duration = [td.text for td in row.find_elements_by_xpath(".//td[8]")]
            distance_travelled = [td.text for td in row.find_elements_by_xpath(".//td[9]")]

            if len(start_addr) > 0 and len(end_addr) > 0:
                start_addr_name = start_addr[0].split('\n')[-2]
                end_addr_name = start_addr[0].split('\n')[-2]
                start_addr = start_addr[0].split('\n')[-1]
                end_addr = end_addr[0].split('\n')[-1]
                trip = {"TripStartAddress": start_addr_name.encode(encoding='UTF-8',errors='strict'), "TripStopAddress": end_addr_name.encode(encoding='UTF-8',errors='strict'), 
                    "LatLngStart": start_addr, "LatLngEnd": end_addr, "Dzongkha": addr[0].encode(encoding='UTF-8',errors='strict'),
                    "AmbulanceNo": ambulance_id, "StartTime": timestamp_from, "EndTime": timestamp_to, 
                    "TripDuration": trip_duration, "DistanceTravelled": distance_travelled}
                df = pd.concat([df, pd.DataFrame(trip, index=[index])])
                index += 1

                # save the results
                try:
                    result = GPSTrip(
                        TripStartAddress=start_addr_name.encode(encoding='UTF-8',errors='strict'),
                        TripStopAddress=end_addr_name.encode(encoding='UTF-8',errors='strict'),
                        LatLngStart=start_addr.decode("utf-8") ,
                        LatLngEnd=end_addr.decode("utf-8") ,
                        Dzongkha=addr[0].encode(encoding='UTF-8',errors='strict'),
                        AmbulanceNo=ambulance_id.decode("utf-8") ,
                        StartTime=timestamp_from.decode("utf-8") ,
                        EndTime=timestamp_to.decode("utf-8") ,
                        TripDuration=trip_duration.decode("utf-8") ,
                        DistanceTravelled=distance_travelled.decode("utf-8") 
                    )
                    db.session.add(result)
                    db.session.commit()
                except:
                    errors.append("Unable to add item to database.")
                
                
        print('Done with this page')
        try:
            pagination = driver.find_element_by_id('page_b')
            links = pagination.find_elements_by_tag_name('li')
            next_link_state = links[-1].get_attribute('class')
            if next_link_state == 'disabled':
                pages_remaining = False
            else:
                time.sleep(5)
                driver.find_element_by_partial_link_text(">").click()
        # edge case in which there is no data available in table
        except NoSuchElementException:
            print('Element could not be found')
            pages_remaining = False
    
    driver.quit()

    if errors:
        return errors
    return str(df)

@app.route("/tt")
def travelTime():
    origins = ["Bobcaygeon ON", [41.43206, -81.38992]]
    destinations = [(43.012486, -83.6964149),
                        {"lat": 42.8863855, "lng": -78.8781627}]
    matrix = gmaps.distance_matrix(origins, destinations, 
                                mode="driving")
    return str(matrix)


@app.route("/gps")
def gps():
    return jsonify(GPSTrip.query.all())

@app.route("/scrape")
def scrape():
    results = {}
    job = q.enqueue_call(
        func=dailyScrape, result_ttl=500000
    )
    print(job.get_id())
    return str(results)

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = GPSTrip.query.filter_by(id=job.result).first()
        return jsonify(result)
    else:
        return "Nay!", 202


@app.route("/scheduler", methods=['GET'])
def monitorer():
    list_of_job_instances = scheduler.get_jobs()
    print(list_of_job_instances)
    return str(list_of_job_instances)

if __name__ == '__main__':
    
    job = scheduler.schedule(
        scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
        func=dailyScrape,                     # Function to be queued
        interval=60,                   # Time before the function is called again, in seconds
        repeat=2,                     # Repeat this number of times (None means repeat forever)
        meta={'foo': 'bar'}            # Arbitrary pickleable data on the job itself
    )
    print("Scheduler: " + job.get_id())
    app.run(debug=True)