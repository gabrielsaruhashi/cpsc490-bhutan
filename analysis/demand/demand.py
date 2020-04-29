import pandas as pd
from datetime import datetime
import re 
import numpy as np
import matplotlib.pyplot as plt 
from IPython.core.debugger import set_trace
import six
import seaborn as sns
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from math import radians, cos, sin, asin, sqrt


# let's load our merged dataset and check its size / columns
df_raw = pd.read_csv("../../preprocessed_data/geographical_units.csv", parse_dates=['Dispatcher_Start'], )

# convert hours to minutes
df_raw['OutgoingTrip_TripDuration_Minutes'] = df_raw.OutgoingTrip_TripDuration.astype(float) / 60
df_raw['ReturnTrip_TripDuration_Minutes'] = df_raw.ReturnTrip_TripDuration.astype(float) / 60

# let's see quantiles to check for anomalies
#print(df_raw.quantile([.05, .95], axis = 0) )

# let's remove the trips with distance travelled 0
df = df_raw[(df_raw['OutgoingTrip_DistanceTravelled'] > 0.3) & (df_raw['OutgoingTrip_TripDuration_Minutes'] < 120)]
df = df[(df_raw['ReturnTrip_DistanceTravelled'] > 0.45) & (df_raw['ReturnTrip_TripDuration_Minutes'] < 120)]
df = df[(df_raw['OutgoingTrip_TripDuration_Minutes'] < df_raw['OutgoingTrip_DistanceTravelled'] * 10)]

geographic_units = pd.read_csv("../../preprocessed_data/fishnet.csv")
geographic_units.index =  np.arange(1, len(geographic_units) + 1)

def calcDistanceToThimpu(gu):
    """
    Input: Lat Longs in string format (e.g "39.3232 40.3232")
    Using the Haversine formula, calculate the great circle distance 
    between two points on the Earth (specified in decimal degrees)
    """
    lat1 = float(gu['Centroid_Latitude'])
    lon1 = float(gu['Centroid_Longitude'])
    
    # Thimpu's location
    lat2 = 27.4661
    lon2 = 89.6419
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    
    return c * r


geographic_units['Distance_Thimpu'] = geographic_units.apply(calcDistanceToThimpu, axis = 1)

df['GU'] = df['OID_1'].astype(int)
df['Hour'] = pd.DatetimeIndex(df['Dispatcher_Start']).hour
df['Month'] = pd.DatetimeIndex(df['Dispatcher_Start']).month

df = df.assign(Season=[0 if x >= 5 and x <= 9 else 1 for x in  pd.DatetimeIndex(df.Dispatcher_Start).month])
df = df.assign(TimeOfDay=[0 if (x >= 0 and x <= 6) else (1 if x > 6 and x <= 12 else (2 if x > 12 and x <= 18 else 3)) for x in df.Hour])
df = df.assign(IsWeekend = [1 if x == 6 or x == 5 else 0 for x in pd.DatetimeIndex(df['Dispatcher_Start']).dayofweek])

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

count = df.groupby(['GU', 'Season', 'TimeOfDay', 'IsWeekend']).count()
levels = [range(1, 22401), range(2), range(4), range(2)]
new_index = pd.MultiIndex.from_product(levels, names=count.index.names)
count = count.reindex(new_index, fill_value=0)

count = count.reset_index()
count = count.iloc[:, 0:5]
count.columns = [*count.columns[:-1], 'Count']

print(count)
def findGU(row, geographic_units):
    print(row)
    gu = geographic_units.loc[geographic_units.index == row['GU']]

    return float(gu['Distance_Thimpu'])

count['Distance_Thimpu'] = count.apply(findGU, args=[geographic_units], axis=1)


X = count.iloc[:, 0:-1]
y= count.iloc[:,-1]


model = Sequential()
model.add(Dense(128, input_dim=4, activation='relu'))
# model.add(Dropout(0.1))
model.add(Dense(128,  activation='relu'))
# model.add(Dropout(0.1))
model.add(Dense(1))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, y, epochs=50, batch_size=10)

print(model.summary())
# evaluate the keras model
_, accuracy = model.evaluate(X, y)
print('Accuracy: %.2f' % (accuracy*100))