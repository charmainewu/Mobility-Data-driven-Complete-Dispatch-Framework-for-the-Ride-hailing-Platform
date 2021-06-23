#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 20:49:29 2021

@author: didi
"""

import networkx as nx
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class MaxMatchOnlWei(object):
    def __init__(self,order,driver,area,uncertainty,interval,seed):
        self.order = order
        self.driver = driver
        self.area = area
        self.n_order = len(order)
        self.n_driver = len(driver)
        self.n_area = len(area)
        self.interval = interval
        self.uncertainty = uncertainty
        self.seed = seed
        
    def getConnectivity(self,DriverList,OrderList,VoidTime,TripWeight):
        driver_time = self.driver[:,1]; driver_area = self.driver[:,0]
        order_start_time = self.order[:,1]; order_start_area = self.order[:,0]
        order_end_time = self.order[:,3]; order_end_area = self.order[:,2]

        driver_list = DriverList; order_list = OrderList; trip_weight = TripWeight
        driver_con_trip = {}; driver_con_area = {}; trip_con_trip = {}
        
        for i in range(len(driver_area)):
            driver_con_trip[i] = []; driver_con_area[i]=[]; 
            max_void_time = driver_time[i]+VoidTime
            min_void_time = driver_time[i]
            
            fil_index = set(np.where((order_start_time < max_void_time) & (order_start_time > min_void_time))[0].tolist()) & set(OrderList)
            for j in fil_index:
                if driver_time[i] + pd.Timedelta(self.area[driver_area[i],order_start_area[j]],unit='s') < order_start_time[j]:
                    driver_con_trip[i].append(j)
        
        for i in range(len(order_end_area)):
            trip_con_trip[i] = []
            max_void_time = order_end_time[i]+VoidTime
            min_void_time = order_end_time[i]
            
            fil_index = set(np.where((order_start_time < max_void_time) 
                                     & (order_start_time > min_void_time))[0].tolist()) & set(OrderList)
            
            for j in fil_index:
                if order_end_time[i] + pd.Timedelta(self.area[order_end_area[i],order_start_area[j]],unit='s') < order_start_time[j]:
                    trip_con_trip[i].append(j)
        
        G = self. buildNetwork(driver_list, order_list, driver_con_trip, trip_con_trip, trip_weight)
        
        return G
    
    def buildNetwork(self, driver_list, order_list, driver_con_trip, trip_con_trip, trip_weight):
        G = nx.DiGraph()
        #add supersource and supersink to the network
        n_driver = len(driver_list)
        G.add_node('s', demand = -n_driver)
        G.add_node('k', demand = n_driver)
        #add drivers to the network
        for i in driver_list:
            G.add_node('dr'+str(i))
        #add trips to the network
        for i in order_list:
            G.add_node('to'+str(i))
            G.add_node('td'+str(i))

        #add edge to supersource and supersink
        for i in driver_list:
            G.add_edge('s','dr'+str(i), weight = 0, capacity = 1)
            G.add_edge('dr'+str(i),'k', weight = 0, capacity = 1)
        
        for i in order_list:
            G.add_edge('td'+str(i),'k', weight = 0, capacity = 1)
            
        #add trips 
        for i,j in zip(order_list, range(len(trip_weight))):
            G.add_edge('to'+str(i),'td'+str(i), weight = -trip_weight[j], capacity = 1)
            #G.add_edge('to'+str(i),'td'+str(i), weight = -1, capacity = 1)
        
        #add driver's connectivity to trip
        for i in driver_con_trip:
            for j in driver_con_trip[i]:
                G.add_edge('dr'+str(i),'to'+str(j), weight = 0, capacity = 1)

        #add trip's connectivity to trip
        for i in trip_con_trip:
            for j in trip_con_trip[i]:
                G.add_edge('td'+str(i),'to'+str(j), weight = 0, capacity = 1)
                    
        #nx.draw(G, with_labels=True)
        #plt.show() 
        return G
    
    def offlineMatch(self,DriverList,TripList,VoidTime,Weight):
        G = self.getConnectivity(DriverList,TripList,VoidTime,Weight)
        flowCost, flowDict = nx.network_simplex(G)
        return -flowCost, flowDict
    
    def findTripList(self,flowDict):
        TripList = sorted([int(u[2:]) for u in flowDict for v in flowDict[u] if flowDict[u][v] > 0 and "to" in u and "td" in v ])
        return TripList
    
    def createDriver(self):
        random.seed(self.seed)
        FDriver = random.sample(range(0,self.n_driver),int(self.uncertainty*self.n_driver))
        CFDriver = set(range(0,self.n_driver))-set(FDriver)
        return CFDriver,FDriver

    def getKeys(self, Dict, Value):
        return [k for k,v in Dict.items() if v == Value]

    def updateDriver(self,DriverList,MatchRoute,BatchEndTime):
        for i in DriverList:
            # find the last trip index
            key = self.getKeys(MatchRoute["dr"+str(i)], 1)
            if 't' not in key[0]:
                continue
            else: 
                while('t' in key[0]):
                    TripzID  = int(key[0][2:])
                    key = self.getKeys(MatchRoute[key[0]],1)
                self.driver[i,1] = self.order[TripzID,3]
                self.driver[i,0] = self.order[TripzID,2]
            """
            # compute left time
            if self.driver[i,1]>BatchEndTime:
                continue
            else:
                LeftTime = int((BatchEndTime - self.driver[i,1])/pd.Timedelta(1,unit='m'))
                # find possible area
                MoveArea = np.where(self.area[self.order[TripzID,2],:] < LeftTime)[0].tolist()
                try:
                    PickArea = random.sample(MoveArea,1)
                    self.driver[i,1] = self.driver[i,1]+pd.Timedelta(self.area[int(self.driver[i,0]),PickArea[0]],unit='s')
                    self.driver[i,0] = PickArea[0]
                except:
                    continue
            """
        return True

    def getFlowCost(self,flowDict):
        TripNum = len([int(u[2:]) for u in flowDict for v in flowDict[u] if flowDict[u][v] > 0 and "to" in u and "td" in v ])
        return TripNum

    def normweight(self,Trip):
        TripWeight = self.order[Trip,4]
        IndexTripWeight = np.argsort(self.order[Trip,1])
        IndexNum = len(IndexTripWeight)
        normTripWeight = np.zeros(IndexNum)
        discount = 1
        
        for i in range(IndexNum):
            Index = IndexTripWeight[-i]
            normTripWeight[Index] = int(TripWeight[Index] * discount**(i))
            sc = MinMaxScaler(feature_range=(0, 3))
            normTripWeight = sc.fit_transform(normTripWeight.reshape(-1,1)).reshape(1,-1)[0].astype(int)
        
        normTripWeight = normTripWeight + 5
        
        return normTripWeight
        
    def twooffMatch(self):
        Trip = range(0,self.n_order)
        CFDriver,FDriver= self.createDriver()
        TotalNum = 0
        
        start_time = min(self.order[:,1]); end_time  = max(self.order[:,1])
        for i in pd.date_range(start = start_time, end = end_time, freq = str(self.interval)+'min'):
            
            interval_start = i; interval_end = i + pd.Timedelta(self.interval,unit='m')
            driverList = np.where(self.driver[:,1] < interval_end)[0].tolist()
            tripList = np.where((self.order[:,1]<interval_end) & (self.order[:,1]>interval_start))[0].tolist()
            
            CFDriver_i = list(set(driverList) & set(CFDriver))
            FDriver_i = list(set(driverList) & set(FDriver))
            Trip_i = list(set(tripList) & set(Trip))
            
            VoidTime = pd.Timedelta(10,unit='m')
            normTripWeight_i = self.normweight(Trip_i)
            OneNum, OneMatch = self.offlineMatch(FDriver_i,Trip_i,VoidTime, normTripWeight_i)
            OneNum = self.getFlowCost(OneMatch)

            VoidTime = pd.Timedelta(20,unit='m')
            UpdateTrip_i = list(set(Trip_i)-set(self.findTripList(OneMatch)))
            normTripWeight_i = self.normweight(UpdateTrip_i)
            TwoNum, TwoMatch = self.offlineMatch(CFDriver_i,UpdateTrip_i,VoidTime,normTripWeight_i)
            TwoNum = self.getFlowCost(TwoMatch)
            IntervalNum = OneNum + TwoNum
            
            self.updateDriver(FDriver_i,OneMatch,interval_end)
            self.updateDriver(CFDriver_i,TwoMatch,interval_end)
            TotalNum = TotalNum + IntervalNum
        return TotalNum
    