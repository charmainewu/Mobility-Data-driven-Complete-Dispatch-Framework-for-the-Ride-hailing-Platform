#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 20:55:42 2021

@author: didi
"""


from learnweight import ComputeWeight
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


order = pd.read_csv("./order.csv")
area = np.load("./area.npy")
order['call_time']=pd.to_datetime(order['call_time']); order['end_time']=pd.to_datetime(order['end_time'])
order = order[['sid','call_time','eid','end_time','real_start_lng','real_start_lat','real_end_lng','real_end_lat']]

for i in range(1,31):
    start_time = '2021-01-'+str(i)+' 06:00:00 AM'; end_time = '2021-01-'+str(i)+' 10:00:00 AM'
    orderdata = order[(order['call_time'] > start_time) & (order['call_time'] < end_time)]
    orderdata = orderdata[['sid','call_time','eid','end_time','real_start_lat','real_start_lng','real_end_lat','real_end_lng']]
    
    train_x_i = pd.DataFrame(columns=['call_day','call_hour','call_minute','end_day','end_hour','end_minute','time','start_lat','start_lng','end_lat','end_lng'])
    train_x_i['call_day'] = orderdata['call_time'].dt.dayofweek
    train_x_i['call_hour'] = orderdata['call_time'].dt.hour
    train_x_i['call_minute'] = orderdata['call_time'].dt.minute
    
    train_x_i['end_day'] = orderdata['end_time'].dt.dayofweek
    train_x_i['end_hour'] = orderdata['end_time'].dt.hour
    train_x_i['end_minute'] = orderdata['end_time'].dt.minute
    
    train_x_i['start_lat'] = orderdata['real_start_lat']
    train_x_i['start_lng'] = orderdata['real_start_lng']
    train_x_i['end_lat'] = orderdata['real_end_lat']
    train_x_i['end_lng'] = orderdata['real_end_lng']
    
    train_x_i['time'] = (orderdata['end_time']-orderdata['call_time'])/pd.Timedelta(1,unit='m')
    #train_x_i['dis'] =  area['sid','eid']
    
    SMM = ComputeWeight(orderdata.values,area)
    train_y_closeness_i = SMM.compTruth()
    
    if i==1:
        train_y_closeness = train_y_closeness_i
        train_x = train_x_i
        order_pick = orderdata[['sid','call_time','eid','end_time']].values
    else:
        train_y_closeness = np.concatenate((train_y_closeness,train_y_closeness_i))
        train_x = np.concatenate((train_x,train_x_i))
        order_pick = np.concatenate((order_pick,orderdata[['sid','call_time','eid','end_time']].values))

np.save("./order_pick.npy",order_pick)
np.save("./train_x_4.npy",train_x)
np.save("./train_y_closeness_4.npy",train_y_closeness)


train_x = np.load("./train_x_4.npy")
train_y_closeness = np.load("./train_y_closeness_4.npy")

enc_w = OneHotEncoder(handle_unknown='ignore')
w1 = enc_w.fit_transform(train_x[:,0].reshape(-1,1)).toarray()

enc_h = OneHotEncoder(handle_unknown='ignore')
h1 = enc_h.fit_transform(train_x[:,1].reshape(-1,1)).toarray()

enc_m = OneHotEncoder(handle_unknown='ignore')
m1 = enc_m.fit_transform(train_x[:,2].reshape(-1,1)).toarray()

enc_w = OneHotEncoder(handle_unknown='ignore')
w2 = enc_w.fit_transform(train_x[:,3].reshape(-1,1)).toarray()

enc_h = OneHotEncoder(handle_unknown='ignore')
h2 = enc_h.fit_transform(train_x[:,4].reshape(-1,1)).toarray()

enc_m = OneHotEncoder(handle_unknown='ignore')
m2 = enc_m.fit_transform(train_x[:,5].reshape(-1,1)).toarray()

for j in range(6,11):
    sc = MinMaxScaler(feature_range=(0, 1))
    train_x[:,j] = sc.fit_transform(train_x[:,j].reshape(-1,1)).reshape(1,-1)
    print(train_x[:,j])

train_x = np.hstack((train_x[:,6:11],m1,w1,h1,m2,w2,h2))


X_train, X_test, y_train, y_test = train_test_split(train_x, train_y_closeness, test_size = 0.1,shuffle=False)
clf_close = MLPRegressor(hidden_layer_sizes = (64,16),learning_rate_init = 0.00001,n_iter_no_change=100,tol=0.00001, max_iter = 1000, random_state=1,verbose = 1).fit(X_train, y_train)
weight_clo = clf_close.predict(X_train)

print(y_train)
print(weight_clo)
print(np.mean(np.abs(y_train-weight_clo)/(y_train+0.1)))
print(clf_close.score(X_train, y_train))

weight_clo = clf_close.predict(X_test)
print(np.mean(np.abs(weight_clo-y_test)/(y_test+0.1)))
print(clf_close.score(X_test, y_test))
sc = MinMaxScaler(feature_range=(1, 10))
weight_clo = sc.fit_transform(weight_clo.reshape(-1,1)).reshape(1,-1)[0]


order_pick = np.load("./order_pick.npy",allow_pickle=True)
order_pick = pd.DataFrame(order_pick)
order_pick.columns = ['sid','call_time','eid','end_time']
orderdata = order_pick.loc[77225:,['sid','call_time','eid','end_time']]
orderdata['clo'] = weight_clo.astype(int)
orderdata.to_csv('./order_clo.csv',index=None)

    
    
    
    