#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 17:16:19 2021

@author: didi
"""

from reopt import MaxMatchOnl
import numpy as np
import pandas as pd

area = np.load("./area.npy")
area = area/40*3600
driver = pd.read_csv("./driver.csv")
order = pd.read_csv("./order.csv")
order['call_time']=pd.to_datetime(order['call_time']); order['end_time']=pd.to_datetime(order['end_time'])
driver['time'] = pd.to_datetime(driver['time'])

k = []

for drivernumber in [0.5]:
    onl_trip = np.zeros((6,5))
    c1 = 0
    for i in range(0,11,2):
        c2 = 0
        for j in [5,10]:
            uncertainty = 0.1*i; seed = 20; interval = 1*j
            
            start_time = pd.to_datetime('2021-01-30 06:00:00 AM'); end_time = pd.to_datetime('2021-01-30 10:00:00 AM')
            order_pick = order[(order['call_time'] > start_time) & (order['call_time'] < end_time)]
            order_pick = order_pick[[ 'sid','call_time','eid','end_time']]
            
            start_time = pd.to_datetime('2021-01-01 09:00:00 AM'); end_time = pd.to_datetime('2021-01-01 10:00:00 AM')
            driver_pick = driver[(driver['time'] > start_time) & (driver['time'] < end_time)]
            driver_pick = driver_pick[['rid','time']]   
            
            driver_pick = driver_pick.iloc[:int(drivernumber*len(order_pick)*0.15)]
            
            driver_pick['time'] = pd.date_range(start=pd.to_datetime('2021-01-30 06:00:00 AM'), end=pd.to_datetime('2021-01-30 10:00:00 AM'), periods=len(driver_pick))
            
            driver_pick = driver_pick.values; order_pick = order_pick.values

            
            SMM = MaxMatchOnl(order_pick,driver_pick,area,uncertainty,interval,seed)
            onl_trip[c1,c2] = SMM.twooffMatch()
            print(onl_trip[c1,c2]); c2 = c2 + 1;
        c1 = c1 + 1;
    print(onl_trip)
    k.append(onl_trip)  
np.save("./data/rep/rep_trip.npy", onl_trip)

