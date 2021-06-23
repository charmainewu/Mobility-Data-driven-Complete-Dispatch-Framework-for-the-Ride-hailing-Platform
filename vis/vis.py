#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 21:39:56 2020

@author: didi
"""

#visualization fig 1

import numpy as np
import matplotlib.pyplot as plt

#sns.set_theme(context='paper', style='whitegrid', palette='deep', font='sans-serif', font_scale=2, color_codes=True, rc=None)
#matplotlib.rcParams['text.usetex'] = True
#plt.style.use('bmh')
plt.rcParams['font.family'] = 'DejaVu Serif'
    

reopt = np.load("./reopt_mean.npy")

##############################################################################
fig, (ax1, ax2) = plt.subplots(1, 2, constrained_layout=False, sharey=False, figsize=(8, 3))

x = np.array([0.0,0.2,0.4,0.6,0.8,1.0])
xx = np.array([10,30,60,120,240])

for i in range(5):
    y = reopt[5]
    ax1.plot(x, y[:,i],label = "B = "+str(xx[i]),marker = '*')

ax1.set_title('Batch Size (min)')
ax1.set_xlabel('Proportion of Part-time Drivers')
ax1.set_ylabel('# Match Order')
ax1.legend(fontsize =7)

x = np.array([0.0,0.2,0.4,0.6,0.8,1.0])
xx = np.array([0.015,0.03,0.045,0.06,0.075,0.09])

for i in range(6):
    y = reopt[i]
    ax2.plot(x, y[:,0], label = "$R_{ndo}$ = "+str(xx[i]),marker = '*')
#ax2.legend(fontsize=7)
ax2.set_xlabel('Proportion of Part-time Drivers')
ax2.set_title('Ratio between Drivers and Orders')

ax2.legend(fontsize = 7)

plt.tight_layout()
plt.savefig("./unc_match.pdf")

##############################################################################
fig, (ax1, ax2) = plt.subplots(1, 2, constrained_layout=False, sharey=False, figsize=(8, 3))

x = np.array([10,30,60,120,240])
xx = np.array([0.0,0.2,0.4,0.6,0.8,1.0])

for i in range(6):
    y = reopt[4]
    ax1.plot(x, y[i,:],label = "$R_{ptd}$ = "+str(xx[i]),marker = '*')

ax1.set_title('Proportion of Part-time Drivers')
ax1.set_xlabel('Batch Size (min)')
ax1.set_ylabel('# Match Order')
ax1.legend(fontsize =7)

x = np.array([10,30,60,120,240])
xx = np.array([0.015,0.03,0.045,0.06,0.075,0.09])

for i in range(6):
    y = reopt[i]
    ax2.plot(x, y[5,:], label = "$R_{ndo}$ = "+str(xx[i]),marker = '*')
#ax2.legend(fontsize=7)
ax2.set_xlabel('Batch Size (min)')
ax2.set_title('Ratio between Drivers and Orders')

ax2.legend(fontsize = 7)

plt.tight_layout()
plt.savefig("./bat_match.pdf")


##############################################################################
fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=False, sharey=False, figsize=(8, 6))

x = np.array([0.015,0.03,0.045,0.06,0.075,0.09])
xx = np.array([0.0,0.2,0.4,0.6,0.8,1.0])

for i in range(0,6,2):
    ax1.plot(x, reopt[:,i,4],label = "$R_{ptd}$ = "+str(xx[i]), marker = '*')

ax1.set_xlabel('Ratio between Drivers and Orders',fontsize = 15)
ax1.set_ylabel('# Match Order',fontsize = 15)
ax1.set_title('Proportion of Part-time Drivers',fontsize = 15)
ax1.legend(fontsize = 15)

x = np.array([0.015,0.03,0.045,0.06,0.075,0.09])
xx = np.array([10,30,60,120,240])

for i in range(0,5,2):
    ax2.plot(x, reopt[:,5,i], label = "B = "+str(xx[i]), marker = 'x')
#ax2.legend(fontsize=7)
ax2.set_xlabel('Ratio between Drivers and Orders',fontsize = 15)
ax2.set_ylabel('# Match Order',fontsize = 15)
ax2.set_title('Batch Size (min)',fontsize = 15)

ax2.legend(fontsize = 15)

plt.tight_layout()
plt.savefig("./dri_match.pdf")


X = []
Y = []
f = []
data = np.load('reopt_mean.npy')
# print(data.shape)
want = data[4]
print(want.shape)
for i in range(6):
    for j in range(5):
        X.append((5-i)*0.2)
        if j==0:
            Y.append(10)
        if j == 1:
            Y.append(30)
        if j == 2:
            Y.append(60)
        if j == 3:
            Y.append(120)
        if j == 4:
            Y.append(240)
        f.append(want[5-i,j])
# for i in range
C = plt.contourf([10,30,60,120,240], [1.0,0.8,0.6,0.4,0.2,0], want,100,cmap='jet')
plt.xlabel("Batch Size")
plt.ylabel("Proportion of Choice-free Drivers")
# plt.clabel(C, inline=True, fontsize=12)
plt.savefig("contourf.pdf", dpi=200, bbox_inches='tight')
plt.show()


    
    


