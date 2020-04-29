# Project Log

## 10/06/2019

Closed Preprocessing and Age issues, formatted the trip duration to seconds. Started working on the analysis. Multiple trips have outgoing or return trips have a 0 distance travelled, need to figure out what's happening there

## 10/13/2019

Went over the preprocessing code again. Grouping Date, AmbulanceNo and PatientName should ensure that we get the right match for multiple potential "outgoing trips", assuming that each ambulance only has one patient with a given name everyday. I also did some auditing on the return trips for the case when there are multiple candidates. It looks like getting the first potential return trip candidate is generally the thing to do. Deleted: dispatch_victim_data_appender.Rmd, moved some old raw files to the archive

## 01/01-2020 - 02/03/2020

Fixed many small bugs, did some cleaning on the facility locaction dataset, created appropriate API endpoints for that
