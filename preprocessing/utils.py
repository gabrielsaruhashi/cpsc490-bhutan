from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
import pandasql as ps
import pdb
from tabulate import tabulate
import re

def viewDf(df):
    print(tabulate(df.head(), headers='keys', tablefmt='psql'))

def saveDF(df, path, index=False):
    df.to_csv(path, index=index)

def unpackLatLng(latlng):
    lats = latlng.str.split().str[0].astype(float)
    lngs = latlng.str.split().str[1].astype(float)
    return lats, lngs

def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'E' or direction == 'N':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    return (lat)

def getDispatcherDataset():
    """
    Merge dispatch records with victim records
    """
    DISPATCH_RECORDS = '../raw_data/dispatch_records_master.csv'
    VICTIM_RECORDS = '../raw_data/victim_details_master.csv'

    df_dispatch = pd.read_csv(DISPATCH_RECORDS)
    getDfInfo(df_dispatch, "Dispatch")
    df_victims = pd.read_csv(VICTIM_RECORDS)
    getDfInfo(df_dispatch, "Victims")

    print("Merging victim and dispatch records to get the complete emergency response information...")

    q1 = """SELECT * FROM df_dispatch
            LEFT JOIN df_victims
            ON  df_dispatch.AmbulanceNo =  df_victims.AmbulanceNo AND 
            df_dispatch.HospitalArrival = df_victims.HospitalArrival"""
    df_er = ps.sqldf(q1, locals())

    # remove duplicate colunmns from merge
    df_er = df_er.loc[:,~df_er.columns.duplicated()]

    # convert start and scene arrival to datetime temporarily (otherwise it will messs up the format)
    start_formatted = pd.to_datetime(df_er.Start, format='%m/%d/%y %H:%M')
    scene_arrival_formatted = pd.to_datetime(df_er.SceneArrival, format='%m/%d/%y %H:%M')

    # response time in minutes
    df_er['ResponseTime'] = (scene_arrival_formatted- start_formatted).astype('timedelta64[s]')

    # remove extra '-' from unique identifier, calculate response time
    df_er['AmbulanceNo'] = df_er['AmbulanceNo'].str.replace("-", "", regex=True).str.strip().str.replace("\s", "", regex=True)
    
    # cast to integer because SQLAlchemy does support datetime
    df_er['StartTimeRaw'] = start_formatted.astype(int)/ 10**9
    df_er.drop_duplicates(inplace=True)

    # assign age NAs to 1000 to avoid being dropped, replace it back later
    df_er.Age = df_er.Age.fillna(1000)
    df_er = df_er.add_prefix('Dispatcher_')

    getDfInfo(df_er, "Hospital ER")
    return df_er

def getGPSDataset():
    # this dataset was scraped from KTracker
    GPS_RECORDS = '../raw_data/scraped_GPS.csv'
    # window size in minutes
    WINDOW = 30
    df_gps = pd.read_csv(GPS_RECORDS)

    # start_time = pd.to_datetime(df_gps.StartTime, format='%Y-%m-%d %H:%M:%S')
    # end_time = pd.to_datetime(df_gps.EndTime, format='%Y-%m-%d %H:%M:%S')
    df_gps['StartTime'] = pd.to_datetime(df_gps.StartTime, format='%Y-%m-%d %H:%M:%S')
    df_gps['EndTime'] = pd.to_datetime(df_gps.EndTime, format='%Y-%m-%d %H:%M:%S')

    df_gps['StartTimeRaw'] = df_gps.StartTime.astype(int)/ 10**9
    df_gps['EndTimeRaw'] = df_gps.EndTime.astype(int)/ 10**9
    df_gps['TimeUpperBound'] = df_gps['StartTimeRaw'] + 60 * WINDOW
    df_gps['TimeLowerBound'] = df_gps['StartTimeRaw'] - 60 * WINDOW
    df_gps['AmbulanceNo'] = df_gps['AmbulanceNo'].str.rsplit("-", n=1).str[0].str.replace("-", "", regex=True).str.strip()
    df_gps['Index'] = pd.Series(range(1, len(df_gps.index)))
    df_gps['TripDuration'] = (df_gps.EndTime - df_gps.StartTime).astype('timedelta64[s]')
    df_gps['LatStart'], df_gps['LngStart'] = unpackLatLng(df_gps.LatLngStart)
    df_gps['LatEnd'], df_gps['LngEnd'] =  unpackLatLng(df_gps.LatLngEnd)

    getDfInfo(df_gps, "Scraped GPS")
    return df_gps

def getHospitalLocations():
    HOSPITAL_LOCATION_RECORDS = '../raw_data/facility_locations.csv'
    df_hospital_locations = pd.read_csv(HOSPITAL_LOCATION_RECORDS)
    df_hospital_locations = df_hospital_locations[['Dzongkhag', 'Hospital / BHU', 'Latitude', 'Longitude', 'Altitude']].dropna(subset=['Hospital / BHU', 'Latitude', 'Longitude']) 
    df_hospital_locations.Latitude = df_hospital_locations.Latitude.astype(str).apply(parse_dms)
    df_hospital_locations.Longitude = df_hospital_locations.Longitude.astype(str).apply(parse_dms)
    df_hospital_locations.columns = map(str.lower, df_hospital_locations.columns)
    return df_hospital_locations


def mergeDatasets(df_er, df_gps):
    # merge outgoing trip with dispatch record
    df_main = ps.sqldf("""SELECT Dispatcher_AmbulanceNo, Dispatcher_DzongkhagName, Dispatcher_HospitalName, 
            Dispatcher_Gender, Dispatcher_Age, Dispatcher_Assigned,  Dispatcher_StartTimeRaw,
            Dispatcher_Start, Dispatcher_SceneArrival, Dispatcher_SceneDeparture,
            Dispatcher_HospitalArrival, Dispatcher_ResponseTime, 
            Dispatcher_VictimName,
            StartTime, EndTime, TripDuration, LatLngStart, LatLngEnd, 
            LatStart, LngStart, LngEnd, LatEnd,
            DistanceTravelled, StartTimeRaw, EndTimeRaw, [Index]
            FROM df_er, df_gps
            WHERE  df_er.Dispatcher_AmbulanceNo = df_gps.AmbulanceNo AND 
            (df_er.Dispatcher_StartTimeRaw BETWEEN df_gps.TimeLowerBound AND 
            df_gps.TimeUpperBound)""", locals())

    df_main.columns = [col if col.startswith('Dispatcher_') else 'OutgoingTrip_' + col for col in df_main]
    df_main['Deviation'] =  df_main.Dispatcher_StartTimeRaw - df_main.OutgoingTrip_StartTimeRaw
    df_main['Date'] = df_main['OutgoingTrip_StartTime'].str.split(" ", n=1).str[0]

    # main can output several outgoing trip matches for the same victim, get the one with min abs deviation
    outgoing_trips = ps.sqldf("""SELECT *, MIN(ABS(Deviation)) as min_deviation 
        FROM df_main 
        GROUP BY Dispatcher_AmbulanceNo, Dispatcher_VictimName, Date""", locals())

    df_final = outgoing_trips.apply(addReturnTripRow, args=(df_gps, df_main), axis=1)

    df_final = df_final.dropna()

    # format datetime columns
    df_final.Dispatcher_Assigned =  pd.to_datetime(df_final.Dispatcher_Assigned, format='%m/%d/%y %H:%M')
    df_final.Dispatcher_Start = pd.to_datetime(df_final.Dispatcher_Start, format='%m/%d/%y %H:%M')
    df_final.Dispatcher_SceneArrival = pd.to_datetime(df_final.Dispatcher_SceneArrival, format='%m/%d/%y %H:%M')
    df_final.Dispatcher_SceneDeparture = pd.to_datetime(df_final.Dispatcher_SceneDeparture, format='%m/%d/%y %H:%M')
    df_final.Dispatcher_HospitalArrival = pd.to_datetime(df_final.Dispatcher_HospitalArrival, format='%m/%d/%y %H:%M')
    df_final.OutgoingTrip_StartTime = pd.to_datetime(df_final.OutgoingTrip_StartTime, format='%Y-%m-%d %H:%M:%S')
    df_final.OutgoingTrip_EndTime = pd.to_datetime(df_final.OutgoingTrip_EndTime, format='%Y-%m-%d %H:%M:%S')
    getDfInfo(df_final, "Merged")

    return df_final

def getDfInfo(df, label):
    print('Size of {} dataset: {}'.format(label, df.shape[0]))

def addReturnTripRow(outgoing_trip, df_gps, df_main):
    """
    Given an outgoing trip, get its return trip based (usually the trip right after)
    """
    potential_return_trips = df_gps.loc[(df_gps['AmbulanceNo'] == outgoing_trip['Dispatcher_AmbulanceNo']) 
        & (df_gps['Index'] > outgoing_trip['OutgoingTrip_Index'])]

    potential_return_trips = potential_return_trips.drop(["AmbulanceNo", "TimeUpperBound","TimeLowerBound"], axis=1)
    potential_return_trips.columns = ["ReturnTrip_" + str(col) for col in potential_return_trips]

    if len(potential_return_trips) == 0:
        cols = np.concatenate([potential_return_trips.columns, outgoing_trip.keys()])
        return np.empty(len(cols)) * np.nan

    return  pd.concat([outgoing_trip, potential_return_trips.iloc[0]])

def calcDistance(latlng1, latlng2):
    """
    Input: Lat Longs in string format (e.g "39.3232 40.3232")
    Using the Haversine formula, calculate the great circle distance 
    between two points on the Earth (specified in decimal degrees)
    """
    lat1 = float(latlng1.split()[0])
    lon1 = float(latlng1.split()[1])
    lat2 = float(latlng2.split()[0])
    lon2 = float(latlng2.split()[1])

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def filterDF(df):
    df_merged = df.apply(filterRecord, axis = 1)
    df_merged = df.dropna()
    
    # place NA ages back, after filtering out the df
    df_merged.loc[df_merged['Dispatcher_Age'] == 1000, 'Dispatcher_Age'] = np.nan
    getDfInfo(df_merged, "Final")
    return df_merged

def filterRecord(row):
    MAX_STOP_DURATION = 12 * 60 * 60 # 12 hours in seconds
    MAX_DISTANCE = 5 # in km

    # if the return trip starts much later than the outgoing one, there's probably something wrong
    if (row['ReturnTrip_StartTimeRaw'] - row['OutgoingTrip_EndTimeRaw']) >= MAX_STOP_DURATION:
        return row.replace(to_replace=r'.*', value=np.nan, regex=True)

    # ensure that the outgoing trip and the return trip are next to each other
    elif calcDistance(row['OutgoingTrip_LatLngEnd'], row['ReturnTrip_LatLngStart']) > MAX_DISTANCE:
        return row.replace(to_replace=r'.*', value=np.nan, regex=True)

    return row


def to_sql_k(self, frame, name, if_exists='fail', index=True,
           index_label=None, schema=None, chunksize=None, dtype=None, **kwargs):
    if dtype is not None:
        from sqlalchemy.types import to_instance, TypeEngine
        for col, my_type in dtype.items():
            if not isinstance(to_instance(my_type), TypeEngine):
                raise ValueError('The type of %s is not a SQLAlchemy '
                                 'type ' % col)

    table = pd.io.sql.SQLTable(name, self, frame=frame, index=index,
                     if_exists=if_exists, index_label=index_label,
                     schema=schema, dtype=dtype, **kwargs)
    table.create()
    table.insert(chunksize)

getHospitalLocations()