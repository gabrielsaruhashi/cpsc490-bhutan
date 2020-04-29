import sqlalchemy as db
import pandas as pd
import collections
import math
import operator
import collections
import math
import operator


def getCurrentAmbulanceDistribution(trips, facilities):
    '''Retrieves the current distribution of ambulances accross the country'''
    mapping = {}
    for hospital, group in trips.groupby(['Dispatcher_HospitalName']):
        mapping[hospital.split()[0].lower()] = len(group['Dispatcher_AmbulanceNo'].unique())
        
    def getAmbulanceCount(row, mapping):
        if row['hospital'] in mapping.keys():
            return mapping[row['hospital']]
        else:
            return 0

    facilities['ambulance_count'] = facilities.apply(getAmbulanceCount, mapping=mapping, axis=1)
    return facilities


def loadData():
    # load trips
    engine = db.create_engine('postgresql://localhost/bhutan', echo=False)
    connection = engine.connect()
    metadata = db.MetaData()
    trips = db.Table('er_trips', metadata, autoload=True, autoload_with=engine)
    query = db.select([trips])

    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    df = pd.DataFrame(ResultSet)
    df.columns = ResultSet[0].keys()


    # load facilities
    facilities = db.Table('facilities', metadata, autoload=True, autoload_with=engine)

    query = db.select([facilities])

    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    df_facilities = pd.DataFrame(ResultSet)
    df_facilities.columns = ResultSet[0].keys()
    df_facilities = df_facilities.rename(columns={"hospital / bhu": "hospital"})

    df_facilities['raw'] = df_facilities.hospital
    df_facilities.hospital = df_facilities.hospital.str.split().str[0].str.lower()
    df_facilities = getCurrentAmbulanceDistribution(df, df_facilities)
    ambulances = len(df['Dispatcher_AmbulanceNo'].unique())
    hospitals = len(df['Dispatcher_HospitalName'].unique())

    print("Total ambulances: %i"%(ambulances))
    print("Total hospitals: %i"%(hospitals))
    distribution = df['Dispatcher_AmbulanceNo'].value_counts()
    print("Current distribution: ")
    print(distribution)

    # load facilities
    return df, df_facilities

# TODO get facilities that are not mapped in the excel sheet and have resources
# for facility in mapping.keys():
#     print(facility)
#     print(mapping[facility])

#     if ((len(df_facilities.loc[df_facilities['hospital'] == facility]) != 0) and 
#         (df_facilities.loc[df_facilities['hospital'] == facility].ambulance_count.values[0] == 0)):
        
#         print(df_facilities.loc[df_facilities['hospital'] == facility]['raw'])




def simulate(events, facilities):
    Candidate = collections.namedtuple('Candidate', 'hospital distance')

    def haversine(coord1, coord2):
        R = 6371  # Earth radius in km
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        phi1, phi2 = math.radians(lat1), math.radians(lat2) 
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + \
            math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        
        return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def calculateHospitalDistance(hospital, event):
        hospital_coords = hospital.latitude, hospital.longitude
        event_coords = event.OutgoingTrip_LatEnd, event.OutgoingTrip_LngEnd     
        return Candidate(hospital=hospital.raw, distance=haversine(hospital_coords, event_coords))

    deltas = []
    ideal_assignment = []
    total = len(events)
    for i, event in events.iterrows():
        print("Simulating event %i/%i"%(i + 1, total))
        # get hospital that was being called
        distances = facilities.apply(calculateHospitalDistance, event=event, axis=1)

        # get hospital with ambulances closest 
        closest_facility = min(distances, key=operator.itemgetter(1))
        ideal_assignment.append(closest_facility)
        
        # get distance to dispatcher hospital name
        assigned_facility = Candidate(hospital=event.Dispatcher_HospitalName,
                                      distance=haversine([event.OutgoingTrip_LatStart, event.OutgoingTrip_LngStart], 
                                      [event.OutgoingTrip_LatEnd, event.OutgoingTrip_LngEnd]))
        
        # ignore possible marginal differences
        if assigned_facility.distance - closest_facility.distance >= 1:
            deltas.append(assigned_facility.distance - closest_facility.distance)
        else:
            deltas.append(0)

    avg_delta = sum(deltas) / len(deltas)
    optimal = sum(deltas == 0) 
    
    print("Average kilometers added by optimal BHU assignment %i"%(avg_delta))
    print("Percentage of optimal assignments %i (%i, %i)", (float(optimal / total), optimal, total ))
    
    
events, facilities = loadData()
simulate(events, facilities)
        