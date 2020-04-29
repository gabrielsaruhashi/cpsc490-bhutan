#!/usr/bin/env python
# coding: utf-8

# In[54]:


import pandas as pd
from datetime import datetime
import re 
import numpy as np
import matplotlib.pyplot as plt 
from IPython.core.debugger import set_trace
import six
import seaborn as sns
get_ipython().magic(u'matplotlib inline')
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


# ### Geographical Units

# In[2]:


geographic_units = pd.read_csv("../../preprocessed_data/fishnet.csv")
geographic_units.index =  np.arange(len(geographic_units))

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



# # Time Series

# In[139]:


data = df.groupby(pd.DatetimeIndex(df['Dispatcher_Start']).date).count()

data = pd.DataFrame({'cnt' : df.groupby( pd.DatetimeIndex(df['Dispatcher_Start']).date ).size()}).reset_index()

# data['Hour'] = df.index.hour
data.columns = ['Date', *data.columns[1:]]

data['Day'] = pd.DatetimeIndex(data.Date).day
data['Month'] =  pd.DatetimeIndex(data.Date).month
data['DayOfWeek'] = pd.DatetimeIndex(data.Date).dayofweek

data = data.assign(Season=[1 if x >= 5 and x <= 9 else 2 for x in  pd.DatetimeIndex(data.Date).month])
# df = df.assign(TimeOfDay=[1 if (x >= 0 and x <= 6) else (1 if x > 6 and x <= 12 else (2 if x > 12 and x <= 18 else 3)) for x in df.Hour])
data = data.assign(IsWeekend = [1 if x == 6 or x == 5 else 0 for x in  pd.DatetimeIndex(data.Date).dayofweek])

print(data)


# In[140]:


train_size = int(len(data) * 0.9)
test_size = len(data) - train_size
train, test = data.iloc[0:train_size], data.iloc[train_size:len(data)]
print(len(train), len(test))


# In[141]:


from sklearn.preprocessing import RobustScaler
sns.lineplot(x=data.Date, y="cnt", data=data);

# cnt_transformer = RobustScaler()
# cnt_transformer = cnt_transformer.fit(train[['cnt']])
# test['cnt'] = cnt_transformer.transform(test[['cnt']])
# train['cnt'] = cnt_transformer.transform(train[['cnt']])



# In[157]:


def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)        
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)


# In[158]:


time_steps = 1

# reshape to [samples, time_steps, n_features]

X_train, y_train = create_dataset(train.iloc[:, 1:], train.cnt, time_steps)
X_test, y_test = create_dataset(test.iloc[:, 1:], test.cnt, time_steps)
print(X_train)
print(X_train.shape, y_train.shape)


# In[159]:


import keras
model = keras.Sequential()
model.add(
  keras.layers.Bidirectional(
    keras.layers.LSTM(
      units=128, 
      input_shape=(X_train.shape[1], X_train.shape[2])
    )
  )
)
model.add(keras.layers.Dropout(rate=0.1))
model.add(keras.layers.Dense(units=1))
model.compile(loss='mean_squared_error', optimizer='adam')


# In[160]:


history = model.fit(
    X_train, y_train, 
    epochs=30, 
    batch_size=32, 
    validation_split=0.1,
    shuffle=False
)


# In[161]:


plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend();


# In[162]:


y_pred = model.predict(X_test)


# In[163]:


plt.plot(y_test.flatten(), marker='.', label="true")
plt.plot(y_pred.flatten(), 'r', label="prediction")
plt.ylabel('Emergency Responses')
plt.xlabel('Time Step')
plt.legend()
plt.show();


# # Geographic Units
# 

# In[3]:


df['GU'] = df['OID_1'].astype(int)
df['Hour'] = pd.DatetimeIndex(df['Dispatcher_Start']).hour
df['Month'] = pd.DatetimeIndex(df['Dispatcher_Start']).month

df = df.assign(Season=[0 if x >= 5 and x <= 9 else 1 for x in  pd.DatetimeIndex(df.Dispatcher_Start).month])
df = df.assign(TimeOfDay=[0 if (x >= 0 and x <= 6) else (1 if x > 6 and x <= 12 else (2 if x > 12 and x <= 18 else 3)) for x in df.Hour])
df = df.assign(IsWeekend = [1 if x == 6 or x == 5 else 0 for x in pd.DatetimeIndex(df['Dispatcher_Start']).dayofweek])


# In[ ]:


#Interpolation
# vals = df['GU'].value_counts()
# df.reset_index()
# x=vals.index
# y=vals.values
# f1 = interpolate.interp1d(vals.index, vals.values,kind = 'linear')
# f2 = interpolate.interp1d(vals.index, vals.values,kind = 'cubic')
# # plt.title('Interpolation for Geographical Unit ' + str(name) )
# plt.plot(x, y, 'o')
# plt.show()


# In[4]:


from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM



# data = df.groupby(['GU', 'Season', 'TimeOfDay', 'IsWeekend', 'Distance_Thimpu']).count().unstack(fill_value=0).stack().reset_index().iloc[:, 0:4]
# data.columns = [*data.columns[:-1], 'Count']



count = df.groupby(['GU', 'Season', 'TimeOfDay', 'IsWeekend']).count()
levels = [range(22401), range(2), range(4), range(2)]
new_index = pd.MultiIndex.from_product(levels, names=count.index.names)
count = count.reindex(new_index, fill_value=0)



count = count.reset_index()
count = count.iloc[:, 0:5]
count.columns = [*count.columns[:-1], 'Count']



def findGU(row, geographic_units):
    gu = geographic_units.loc[geographic_units.index == row['GU']]
    print(gu['Distance_Thimpu'])
    print(row)
    return float(gu['Distance_Thimpu'])

count['Distance_Thimpu'] = count.apply(findGU, args=[geographic_units], axis=1)
# sns.pointplot(data=df, x='Hour', y='Count', ax=ax1)
# sns.pointplot(data=df, x='Hour', y='Count', hue='Season', ax=ax2)
# sns.pointplot(data=data, x='Hour', y='Count', hue='TimeOfDay', ax=ax3)

# fig,(ax1, ax2, ax3, ax4)= plt.subplots(nrows=4)
# fig.set_size_inches(18, 28)




# In[6]:


X = data.iloc[:, 0:-1]
y= data.iloc[:,-1]


model = Sequential()
model.add(Dense(128, input_dim=4))
model.add(Activation('relu'))
model.add(Dropout(0.1))

model.add(Dense(128))
model.add(Activation('relu'))
model.add(Dropout(0.1))
model.add(Dense(1))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, y, epochs=150, batch_size=10)

print(model.summary())
# evaluate the keras model
_, accuracy = model.evaluate(X, y)
print('Accuracy: %.2f' % (accuracy*100))


# In[11]:


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


# In[56]:


scaler = StandardScaler()

X = pd.concat([count.iloc[:, 1:4], count.iloc[:, 5]], axis=1)
X['Distance_Thimpu'] = scaler.fit_transform(X[['Distance_Thimpu']])

y = count.iloc[:,4]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)


# In[42]:


from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils import compute_sample_weight

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import SGD



model = Sequential()
model.add(Dense(128, input_dim=4, activation='relu'))
model.add(Dense(128, activation='relu'))

# model.add(Dropout(0.1))
# model.add(Dropout(0.1))
model.add(Dense(1))

weights = compute_sample_weight(class_weight="balanced", y=y_train)
print(np.unique(weights))

sgd = SGD(lr=0.01)

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
history = model.fit(X_train, y_train,
                    batch_size=32,
                    epochs=50,
                    verbose=1,
                    validation_data=(X_test, y_test),
                    sample_weight=weights)

score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

print(model.summary())
# evaluate the keras model
# _, accuracy = model.evaluate(X, y)
# print('Accuracy: %.2f' % (accuracy*100))


# In[43]:


score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

print(model.summary())
# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


# # Categorical

# In[58]:


unique, counts = np.unique(y, return_counts=True)
prob = np.asarray((unique, counts)).T

fig = plt.figure()
ax = fig.add_axes([0,0,1,1])

print(prob)
ax.bar(unique, counts)
plt.xticks(rotation=25)
plt.show()


# In[61]:


y_cat = [x if x == 0 else 1 if x == 1 else 2 if (x >= 2 and x < 5) else 3 if (x >= 5 and x < 10) else 4 for x in y]

print(np.unique(y_cat, return_counts=True))

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.20)


# In[65]:



model = Sequential()
model.add(Dense(128, input_dim=4, activation='relu'))
model.add(Dense(128, activation='relu'))

# model.add(Dropout(0.1))
# model.add(Dropout(0.1))
model.add(Dense(5, activation='softmax'))

weights = compute_sample_weight(class_weight="balanced", y=y_train)
print(np.unique(weights))

sgd = SGD(lr=0.01)

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(X_train, y_train,
                    batch_size=32,
                    epochs=50,
                    verbose=1,
                    validation_data=(X_test, y_test),
                    sample_weight=weights)

score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

print(model.summary())


# In[69]:


print(history.history)
print(model.summary())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()




