# Log

### Demand model

We consider two time periods because emergency demand is known to follow a circadian rhythm (Bagai et al. 2013, McCormack and Coates 2015), meaning that demand is much higher during the day than at night. We consider two modes of transport because of the multi-modal nature of decentralized ambulance services in LMICs.

# Folder structure

## App

The backend and frontend of our application

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

## Preprocessed Data

Merged data after preprocessing

## Analysis

All the statistical analysis performed on the preprocessed data

# TODO

## Backend

- [x] Setup python backend to automate scraping
- [ ] Setup actual cron-like schedule job

## Frontend

- [x] Discovery why return trips all have same lat. Once I figure that out, plot on Kepler the appropriate return trip
- [x] Build the maps and static charts on the frontend
- [x] Add Kepler map
- [x] Setup architecture of frontend
- [x] Setup dummy navbar for reference
- [x] Override default font (CircularStd)
- [ ] Add filter for summary according to month
- [ ] Add icons to cards
- [ ] Add kepler map to menu (add react router and set up routes)
- [ ] Customer development with stakeholders
      <<<<<<< HEAD
- [ ] # Functionality to create custom grids and export data (fishnet ArcGIS)
  > > > > > > > cdd88f6b67081a8ac9139edf4706e6121a3c15ef

## Analysis

- [ ] Finish plotting stuff for paper
- [ ] Plot % of response time that hit goal

## Optimization

- [x] Literature review for paper
- [x] Travel Time
- [x] Create GU on ArcGIS
- [x] Interpolations for every GU
- [ ] Draw out mathematical model
