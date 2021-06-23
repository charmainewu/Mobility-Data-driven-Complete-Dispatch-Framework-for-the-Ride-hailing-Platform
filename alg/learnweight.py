#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 16:04:29 2021

@author: didi
"""


import networkx as nx
import numpy as np
import pandas as pd


class ComputeWeight(object):
    def __init__(self,order,area):
        self.order = order
        self.area = area
        self.n_order = len(order)
        self.n_area = len(area)
        
    def getConnectivity(self,OrderList,VoidTime):
        order_start_time = self.order[:,1]; order_start_area = self.order[:,0]
        order_end_time = self.order[:,3]; order_end_area = self.order[:,2]

        order_list = OrderList
        trip_con_trip = {}
        
        for i in range(len(order_end_area)):
            trip_con_trip[i] = []
            max_void_time = order_end_time[i]+VoidTime
            min_void_time = order_end_time[i]
            
            fil_index = set(np.where((order_start_time < max_void_time) 
                                     & (order_start_time > min_void_time))[0].tolist()) & set(OrderList)
            
            for j in fil_index:
                if order_end_time[i] + pd.Timedelta(self.area[order_end_area[i],order_start_area[j]],unit='s') < order_start_time[j]:
                    trip_con_trip[i].append(j)
        
        G = self.buildNetwork(order_list, trip_con_trip)
        
        return G
    
    def buildNetwork(self, order_list, trip_con_trip):
        G = nx.DiGraph()
        order_start_area = self.order[:,0]
        order_end_area = self.order[:,2]

        #add trips to the network
        for i in order_list:
            G.add_node('to'+str(i))
            #G.add_node('td'+str(i))


        #add trip's connectivity to trip
        for i in trip_con_trip:
            for j in trip_con_trip[i]:
                G.add_edge('to'+str(i),'to'+str(j), distance = self.area[order_end_area[i],order_start_area[j]])
                    
        #nx.draw(G, with_labels=True)
        #plt.show()
        return G
    
    def compTruth(self):
        TripList = range(0,self.n_order)
        VoidTime = pd.Timedelta(10,unit='m')
        G = self.getConnectivity(TripList,VoidTime)
        clo = nx.closeness_centrality(G)
        
        closeness = np.zeros(len(clo))
        
        for i in TripList:
            closeness[i] = float(clo["to"+str(i)])
        
        return closeness


        
    