#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 21:26:30 2021

@author: didi
"""


import networkx as nx
import random
import numpy as np
import pandas as pd

class MaxMatchOff(object):
    def __init__(self,order,driver,area,uncertainty,seed):
        self.order = order
        self.driver = driver
        self.area = area
        self.n_order = len(order)
        self.n_driver = len(driver)
        self.n_area = len(area)
        self.uncertainty = uncertainty
        self.seed = seed
        
    def getConnectivity(self,DriverList,OrderList,VoidTime):
        driver_time = self.driver[:,1]; driver_area = self.driver[:,0]
        order_start_time = self.order[:,1]; order_start_area = self.order[:,0]
        order_end_time = self.order[:,3]; order_end_area = self.order[:,2]

        driver_list = DriverList; order_list = OrderList
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
        
        G = self. buildNetwork(driver_list, order_list, driver_con_trip, trip_con_trip)
        
        return G
    
    def buildNetwork(self, driver_list, order_list, driver_con_trip, trip_con_trip):
        G = nx.DiGraph()
        #add supersource and supersink to the network
        n_driver = len(driver_list)
        G.add_node('s', demand = -n_driver)
        G.add_node('t', demand = n_driver)
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
            G.add_edge('dr'+str(i),'t', weight = 0, capacity = 1)
        
        for i in order_list:
            G.add_edge('td'+str(i),'t', weight = 0, capacity = 1)
            
        #add trips 
        for i in order_list:
            G.add_edge('to'+str(i),'td'+str(i), weight = -1, capacity = 1)
        
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
    
    def offlineMatch(self,DriverList,TripList,VoidTime):
        G = self.getConnectivity(DriverList,TripList,VoidTime)
        flowCost, flowDict = nx.network_simplex(G)
        return -flowCost, flowDict
    
    def findTripList(self,flowDict):
        TripList = sorted([int(u[2:]) for u in flowDict for v in flowDict[u] if flowDict[u][v] > 0 and "to" in u and "td" in v ])
        return TripList
    
    def createDriver(self):
        FDriver = random.sample(range(0,self.n_driver),int(self.uncertainty*self.n_driver))
        CFDriver = set(range(0,self.n_driver))-set(FDriver)
        return CFDriver,FDriver
        
    def twooffMatch(self):
        TripList = range(0,self.n_order)
        CFDriver,FDriver= self.createDriver()
        
        VoidTime = pd.Timedelta(10,unit='m')
        OneNum, OneMatch = self.offlineMatch(FDriver,TripList,VoidTime)
        print(OneNum)

        VoidTime = pd.Timedelta(20,unit='m'); UpdateTripList = list(set(TripList)-set(self.findTripList(OneMatch)))
        print(len(self.findTripList(OneMatch)))
        TwoNum, TwoMatch = self.offlineMatch(CFDriver,UpdateTripList,VoidTime)
        print(TwoNum)
        
        
        TotalNum = OneNum + TwoNum
        return TotalNum

        
        
        
        