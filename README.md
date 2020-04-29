# Acknowledgements
A warm thank you for Dr. Sanjay Aneja for helping me so much this semester :)

# Folder structure

## App

The backend and frontend of our dashboard application

## Scraping

Scrapes GPS data from the KTracker website

## Raw Data

All the raw data obtained from 1)scraping and 2) hospital

- Size of Dispatch dataset: 7901
- Size of Victims dataset: 7901
- Size of Scraped GPS dataset (July 1 2018 - March 31 2019): 68264

## Preprocessing

Given the raw GPS data scraped from KTracker and the dispatch records sent from the hospital in XLXS format, merge each emergency response to its respective outgoing and returning trip (according to GPS data)

Output:

- 3034 emergency response records (38.4% of matches)

Here you can find the Flask server as well that enqueues crawl requests.

## Preprocessed Data

Merged data after preprocessing

## Analysis

All the statistical analysis performed on the preprocessed data. Here you can find the machine learning models as well.
