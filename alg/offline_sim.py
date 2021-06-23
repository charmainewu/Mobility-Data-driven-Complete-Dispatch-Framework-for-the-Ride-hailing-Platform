#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 16:16:26 2021

@author: didi
"""

from offline import MaxMatchOff
import numpy as np
import pandas as pd
import random


driver = pd.read_csv("./driver.csv")
order = pd.read_csv("./order.csv")
area = np.load("./area.npy")
off_trip = np.zeros(5); count = 0
order['call_time']=pd.to_datetime(order['call_time']); order['end_time']=pd.to_datetime(order['end_time'])
driver['time'] = pd.to_datetime(driver['time'])
area = area/40*3600

for i in range(1,11,2):
    uncertainty = 0; seed = 20
    start_time = pd.to_datetime('2021-01-30 06:00:00 AM'); end_time = pd.to_datetime('2021-01-30 10:00:00 AM')
    order_pick = order[(order['call_time'] > start_time) & (order['call_time'] < end_time)]
    order_pick = order_pick[[ 'sid','call_time','eid','end_time']]
    
    start_time = pd.to_datetime('2021-01-01 09:00:00 AM'); end_time = pd.to_datetime('2021-01-01 10:00:00 AM')
    driver_pick = driver[(driver['time'] > start_time) & (driver['time'] < end_time)]
    driver_pick['time'] = pd.date_range(start=pd.to_datetime('2021-01-30 06:00:00 AM'), end=pd.to_datetime('2021-01-30 10:00:00 AM'), periods=len(driver_pick))
    driver_pick = driver_pick[['rid','time']]
    
    driver_pick = driver_pick.values; order_pick = order_pick.values
    #random.seed(seed)                                                                                                
    #unc_driver_true = random.sample(range(0,len(driver_pick)),int(len(driver_pick)*uncertainty))       
    unc_driver_true = range(400)
    print(len(unc_driver_true))
    print(len(order_pick))
    driver_pick = driver_pick[unc_driver_true,:]   
    
    SMM = MaxMatchOff(order_pick,driver_pick,area,uncertainty,seed)
    off_trip[count] = SMM.twooffMatch()
    print(off_trip[count]); count = count + 1

np.save("./data/off/off_trip.npy", off_trip)














