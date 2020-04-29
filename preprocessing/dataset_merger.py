import pandas as pd
import datetime
import pandasql as ps
import re
from utils import *
from sqlalchemy import create_engine
from sqlalchemy.types import *

# this dataset was obtained from the hospital
df_er = getDispatcherDataset()
saveDF(df_er, "../preprocessed_data/merged_patient_trips.csv")

# this is the dataset we scraped from KTracker
df_gps = getGPSDataset()
saveDF(df_gps, "../preprocessed_data/processed_gps_data.csv")

df_merged = mergeDatasets(df_er, df_gps)
df_merged = filterDF(df_merged)

# drop extraneous columns
df_merged = df_merged.drop(columns=["Dispatcher_StartTimeRaw", "OutgoingTrip_StartTimeRaw", "OutgoingTrip_EndTimeRaw", 
            "OutgoingTrip_Index", "min_deviation", "Deviation", "Date", "ReturnTrip_StartTimeRaw", "ReturnTrip_EndTimeRaw",
            "ReturnTrip_Index", "ReturnTrip_TripStopAddress", "ReturnTrip_TripStartAddress", "Dispatcher_VictimName", 
            "ReturnTrip_LatLngStart", "ReturnTrip_LatLngEnd", "OutgoingTrip_LatLngStart", "OutgoingTrip_LatLngEnd"])
saveDF(df_merged, "../preprocessed_data/merged_ktracker_30min.csv")

print(df_merged.dtypes)

# store SQL databse
engine = create_engine('postgresql://localhost/bhutan', echo=False)
print("Overwriting SQL database")

pandas_sql = pd.io.sql.pandasSQL_builder(engine, schema=None)
to_sql_k(pandas_sql, df_merged, 'er_trips',
        index=True, keys='index', if_exists='replace')

# store hospital locations in another table
df_hospital_locations = getHospitalLocations()
saveDF(df_hospital_locations, "../preprocessed_data/clean_hospital_locations.csv")
print("Storing hospital locations in SQL database")
to_sql_k(pandas_sql, df_hospital_locations, 'facilities',
        index=True, keys='index', if_exists='replace')

