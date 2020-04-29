#Importing packages
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
import sys 


def generateURL(start_date, end_date):
    print("Generating url for the week of " + str(start_date) + " to " +str(end_date))
    BASE_URL = 'http://www.ktracker.bt/report/trip?r_uin%5B%5D=__all_sub&r_date_time_type=1&r_date='
    return BASE_URL + \
        str(start_date) + '+00%3A00+-+' + str(end_date) + \
        '+00%3A00&r_judge=1&r_page_size=100&r_drtn=2&_k=&r_search='
     
# initialize driver
driver = webdriver.Chrome('./chromedriver')


# login and get access credentials
driver.get('http://www.ktracker.bt/')
username = driver.find_element_by_id("loginAccount").send_keys("hhc")
password = driver.find_element_by_id("loginPassword").send_keys("hhc123")
driver.find_element_by_xpath("//button[@type='submit']").click()

# pick the date ranges
START_DATE = datetime.strptime(input('What is the start date? (e.g 2019-3-26)\n' ), "%Y-%m-%d")
END_DATE = datetime.strptime(input('What is the end date? (e.g 2019-3-26)\n' ), "%Y-%m-%d")

WINDOW = 1
current_date_range = START_DATE


# Start point 2020-02-28 
CHECKPOINT_FILE = './output/GPS_2020-01-24_2020-03-21.csv'
df = pd.read_csv(CHECKPOINT_FILE)

# define main data frame that will store 
index = len(df.index)

while current_date_range <= END_DATE:
    url = generateURL(current_date_range.date(), (current_date_range + timedelta(days=WINDOW)).date())
    driver.get(url)

    pages_remaining = True
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
                trip_row = pd.DataFrame(trip)
                df = pd.concat([df, pd.DataFrame(trip, index=[index])])
                index += 1
                
        print('Done with this page')
        try:
            pagination = driver.find_element_by_id('page_b')
            links = pagination.find_elements_by_tag_name('li')
            next_link_state = links[-1].get_attribute('class')
            if next_link_state == 'disabled':
                pages_remaining = False
            else:
                time.sleep(5)
                next_link = driver.find_element_by_partial_link_text(">").click()
        # edge case in which there is no data available in table
        except NoSuchElementException:
            print('Element could not be found')
            pages_remaining = False
    
    # overwrite previous checkpoint
    print('Saving progress...')
    df.to_csv(CHECKPOINT_FILE)
    #df.to_csv("./output/GPS_" + str(START_DATE.strftime("%Y-%m-%d")) + "_" + str(END_DATE.strftime("%Y-%m-%d")) + ".csv", index=False)

    # update date range for next iteration
    current_date_range += timedelta(days=WINDOW)

driver.quit()
      