# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 17:33:10 2019

@author: robby
"""

import numpy as np
import pandas as pd
import random
import math
from timeit import default_timer as timer

baca_data = pd.read_csv('yor-f-83.stu', delimiter=' ', names=list(range(20))).dropna(axis='columns', how='all')

baca_data = baca_data.fillna(-1)

baca_data.iloc[:,:len(baca_data.columns)] = baca_data.iloc[:,:len(baca_data.columns)].values.astype(int)

arr = np.zeros((baca_data.max().max(), baca_data.max().max()))
arr = pd.DataFrame(arr).values.astype(int)

for i in range(0, len(baca_data)):
    k=0
    l=0
    j=1
    while j!=len(baca_data.columns):
        z = j+l
        if baca_data.iloc[i,k]!=-1 and baca_data.iloc[i,z]!=-1:
            arr[baca_data.iloc[i,k]-1][baca_data.iloc[i,z]-1] += 1
            arr[baca_data.iloc[i,z]-1][baca_data.iloc[i,k]-1] += 1
        if z==len(baca_data.columns)-1:
            k += 1
            l += 1
            j = 0
        if k==len(baca_data.columns)-1:
            break
        j += 1

arr = pd.DataFrame(arr)

# testing

degree = []

for i in range(len(arr)):
    num = 0
    for j in range(len(arr)):
        if arr.iloc[i,j]!=0 :
            num+=1
    degree.append(num)
        
degree = pd.DataFrame(degree)        

sorting_degree = pd.DataFrame(degree[0].sort_values(ascending=False))
       
arr2 = pd.DataFrame(index = sorting_degree.index)
for i in range(len(arr.columns)):
    arr3 = pd.DataFrame(index = sorting_degree.index, data=arr.iloc[:,sorting_degree.index[i]])
    arr2 = pd.concat([arr2,arr3], axis=1)
    

# -------------- lARGEST DEGREE --------------------------------------------- #
List = pd.DataFrame([], columns=['ts'])
for i in range(len(arr2)):
    for j in range(len(arr2.columns)):
        if List.index[List['ts']==j].size>0:
            z=0
            for m in List.index[List['ts']==j]:
                if arr2.loc[arr2.index[i],m]!=0:
                    z+=1
            if z==0:
                List = List.append(pd.DataFrame([j], columns=['ts'], index=[arr2.index[i]]))
                break
        elif List.index[List['ts']==j].size==0:
            if List['ts'].size==0:
                List = List.append(pd.DataFrame([0], columns=['ts'], index=[arr2.index[i]]))
                break
            elif List['ts'].size>0:
                List = List.append(pd.DataFrame([max(List['ts'])+1], columns=['ts'], index=[arr2.index[i]]))
                break
            
# --------------------------------------------------------------------------- #
timeslot = []
for i in range(max(List['ts'])+1):
    timeslot.append(List.index[List['ts']==i].values)    
# --------------------------------------------------------------------------- #  
pinalty_temp = []
for i in range(len(sorting_degree.index)):
    for j in range(i+1, len(sorting_degree.index)):
        student = arr2.loc[sorting_degree.index[i], sorting_degree.index[j]]
        weight = 2**(5-abs(List.loc[sorting_degree.index[i],'ts']-List.loc[sorting_degree.index[j],'ts']))
        pinalty_temp.append(student*weight)

pinalty = sum(pinalty_temp)/len(baca_data)
# --------------------------------------------------------------------------- #
#Hill Climbing
start = timer()

trajectory_hc = []
List_temp_hc = List.copy()
hill_climbing_pinalty = pinalty.copy()
for i in range(1000):
    x = random.randint(0, max(List_temp_hc.index))
    y = random.randint(0, max(List_temp_hc['ts']))
    List_temp_hc.loc[x,'ts'] = y
    z=0
    print("i= "+str(i), 'x= '+str(x), 'y= '+str(y))
    for k in List_temp_hc.index[List_temp_hc['ts']==y]:
        if arr2.loc[x,k]!=0:
            List_temp_hc.loc[x,'ts'] = List.loc[x,'ts']
            z+=1
            break
    if z==0:
        pinalty_temp = []
        for o in range(len(sorting_degree.index)):
            for p in range(o+1, len(sorting_degree.index)):
                student = arr2.loc[sorting_degree.index[o], sorting_degree.index[p]]
                weight = 2**(5-abs(List_temp_hc.loc[sorting_degree.index[o],'ts']-List_temp_hc.loc[sorting_degree.index[p],'ts'])).astype(float)
                pinalty_temp.append(student*weight)
        new_pinalty = sum(pinalty_temp)/len(baca_data)
        trajectory_hc.append(new_pinalty)
        print('new_pinalty= '+str(new_pinalty), 'pinalty= '+str(hill_climbing_pinalty))
        if hill_climbing_pinalty > new_pinalty:
            hill_climbing_pinalty = new_pinalty.copy()
        elif hill_climbing_pinalty < new_pinalty:
            List_temp_hc.loc[x,'ts'] = List.loc[x,'ts']

end = timer()
print(str(end-start))

# convert trajectory_hc to dataframe
trajectory_hc = pd.DataFrame(trajectory_hc)
# Create trajectory_hc line chart
trajectory_hc.plot.line()
# --------------------------------------------------------------------------- #

delta_hc = "{:.1%}".format(abs((hill_climbing_pinalty-pinalty)/pinalty))

# --------------------------------------------------------------------------- #
#Simulated Annaling
start = timer()

trajectory_sa = []
List_temp_sa = List.copy()
sa_pinalty = pinalty.copy()
T = 0.999
for i in range(1000):
    x = random.randint(0, max(List_temp_sa.index))
    y = random.randint(0, max(List_temp_sa['ts']))
    
    List_temp_sa.loc[x,'ts'] = y
    
    z=0
    print("i= "+str(i), 'T= '+str(T), 'x= '+str(x), 'y= '+str(y))
    for k in List_temp_sa.index[List_temp_sa['ts']==y]:
        if arr2.loc[x,k]!=0:
            List_temp_sa.loc[x,'ts'] = List.loc[x,'ts']
            z+=1
            break
    
    if z==0:
        pinalty_temp = []
        for o in range(len(sorting_degree.index)):
            for p in range(o+1, len(sorting_degree.index)):
                student = arr2.loc[sorting_degree.index[o], sorting_degree.index[p]]
                weight = 2**(5-abs(List_temp_sa.loc[sorting_degree.index[o],'ts']-List_temp_sa.loc[sorting_degree.index[p],'ts'])).astype(float)
                pinalty_temp.append(student*weight)
        new_pinalty = sum(pinalty_temp)/len(baca_data)
        trajectory_sa.append(new_pinalty)
        if sa_pinalty > new_pinalty:
            sa_pinalty = new_pinalty.copy()
        else:
            prob = math.exp(-(abs(new_pinalty-sa_pinalty)/T))
            r = random.uniform(0,1)
            print("prob= "+str(prob), 'r= '+str(r), 'new_pinalty= '+str(new_pinalty), 'pinalty= '+str(sa_pinalty))
            if prob > r:
                sa_pinalty = new_pinalty.copy()
            else:
                List_temp_sa.loc[x,'ts'] = List.loc[x,'ts']
    T -= 0.00099

end = timer()
print(str(end-start))

# convert trajectory_hc to dataframe
trajectory_sa = pd.DataFrame(trajectory_sa)
# Create trajectory_hc line chart
trajectory_sa.plot.line()
# --------------------------------------------------------------------------- #

delta_sa = "{:.1%}".format(abs((sa_pinalty-hill_climbing_pinalty)/hill_climbing_pinalty))

# --------------------------------------------------------------------------- #
#VNS
start = timer()

trajectory_vns = []
List_temp_vns = List.copy()
vns_pinalty = pinalty.copy()
for i in range(1000):
    h = 0
    if h==0:
        x = random.randint(0, len(timeslot))
        y = random.randint(0, len(timeslot))
        
        exam_set1 = List_temp_vns.index[List['ts']==x]
        exam_set2 = List_temp_vns.index[List['ts']==y]

        temp1, temp2 = [], []
        for c in exam_set1:
            for d in exam_set2:
                if arr.loc[c,d]!=0:
                    if c not in temp1:
                        temp1.append(c)
                    if d not in temp2:
                        temp2.append(d)
        List_temp_vns.loc[temp1, 'ts'] = y
        List_temp_vns.loc[temp2, 'ts'] = x    

        pinalty_temp = []
        for o in range(len(sorting_degree.index)):
            for p in range(o+1, len(sorting_degree.index)):
                student = arr2.loc[sorting_degree.index[o], sorting_degree.index[p]]
                weight = 2**(5-abs(List_temp_vns.loc[sorting_degree.index[o],'ts']-List_temp_vns.loc[sorting_degree.index[p],'ts'])).astype(float)
                pinalty_temp.append(student*weight)
        new_pinalty = sum(pinalty_temp)/len(baca_data)
        trajectory_vns.append(new_pinalty)
        print(h, vns_pinalty, new_pinalty, i)
        if vns_pinalty > new_pinalty:
            vns_pinalty = new_pinalty.copy()
        if vns_pinalty < new_pinalty:
            List_temp_vns.loc[temp1, 'ts'] = x
            List_temp_vns.loc[temp2, 'ts'] = y
            h=1
    if h==1:
        x = random.randint(0, max(List_temp_vns.index))
        y = random.randint(0, max(List_temp_vns['ts']))
        List_temp_vns.loc[x,'ts'] = y
        z=0
        for k in List_temp_vns.index[List_temp_vns['ts']==y]:
            if arr2.loc[x,k]!=0:
                List_temp_vns.loc[x,'ts'] = List.loc[x,'ts']
                z+=1
                break
        if z==0:
            pinalty_temp = []
            for o in range(len(sorting_degree.index)):
                for p in range(o+1, len(sorting_degree.index)):
                    student = arr2.loc[sorting_degree.index[o], sorting_degree.index[p]]
                    weight = 2**(5-abs(List_temp_vns.loc[sorting_degree.index[o],'ts']-List_temp_vns.loc[sorting_degree.index[p],'ts'])).astype(float)
                    pinalty_temp.append(student*weight)
            new_pinalty = sum(pinalty_temp)/len(baca_data)
            trajectory_vns.append(new_pinalty)
            print(h, vns_pinalty, new_pinalty, i)
            if vns_pinalty > new_pinalty:
                vns_pinalty = new_pinalty.copy()
            if vns_pinalty < new_pinalty:
                List_temp_vns.loc[x,'ts'] = List.loc[x,'ts']
                h=0

end = timer()
print(str(end-start))
# convert trajectory_hc to dataframe
trajectory_vns = pd.DataFrame(trajectory_vns)
# Create trajectory_hc line chart
trajectory_vns.plot.line()
# --------------------------------------------------------------------------- #

delta_sa = "{:.1%}".format(abs((vns_pinalty-sa_pinalty)/sa_pinalty))

# --------------------------------------------------------------------------- #
List_temp_vns['index'] = List_temp_vns.index
List_temp_vns = List_temp_vns[['index', 'ts']]

List_temp_vns.sort_values(by=['index'], inplace=True)
List_temp_vns['index'] += 1
#List['ts'] += 1   
        
List_temp_vns.to_csv('EdHEC92.sol', header=False, index=False, sep=' ') 
# --------------------------------------------------------------------------- #
  