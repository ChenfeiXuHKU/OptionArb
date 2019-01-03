# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 14:35:25 2019

@author: chenf
"""
from __future__ import division
import pandas as pd
from datetime import datetime 
from collections import OrderedDict
from datetime import timedelta
import os

def PredictData(begin, end, dim):
    
    while begin != end:

        Predict_data = OrderedDict() 
        Predict_data_pd = pd.DataFrame()  
        data = pd.read_csv('../option_data/option_' + begin + '.csv')
        #for call options one day
        for i in range(len(data)):
            code = data.loc[i,'Option Code']
            if data.loc[i,'Change(C%)'] == '-':
                continue
            if data.loc[i,'Change(HSIo,C%)'] == '-':
                continue
                
            inputs = []    
            days = 0
            temp_date = begin
            while(days < dim):
                #search previous trading day
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
                while((not os.path.exists('../option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                u_time = last_date[0:10]
                last_data = pd.read_csv('../option_data/option_' + u_time + '.csv')
                   
                #get max change value at that day
                changes_c = last_data['Change(C%)'].tolist()
                while '-' in changes_c:
                    changes_c.remove('-')
                temp_changes_c_max = max([float(cc) for cc in changes_c])
                temp_changes_c_min = min([float(cc) for cc in changes_c])
                #get change value for one option at that day
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                if last_data.loc[last_index,'Change(C%)'] == '-':
                    break
                else:
                    temp_C_change = float(last_data.loc[last_index,'Change(C%)'])  
                #normalize change value and store
                if temp_changes_c_max == 0:
                    c_scale = abs(temp_changes_c_min)
                    inputs.append(temp_C_change / c_scale)        
                elif temp_changes_c_min == 0:
                    c_scale = abs(temp_changes_c_max)
                    inputs.append(temp_C_change / c_scale)
                else:
                    if temp_C_change >= 0:
                        c_scale = abs(temp_changes_c_max)
                    else:
                        c_scale = abs(temp_changes_c_min)
                    inputs.append(temp_C_change / c_scale)

                #get max volume at that day
                volumes_c = last_data['Volume(C)'].tolist()
                while '-' in volumes_c:
                    volumes_c.remove('-')
                temp_c_vol_max = max([int(str(vc).replace(',','')) for vc in volumes_c])    
                #get volume for above option at that day
                if last_data.loc[last_index,'Volume(C)'] == '-':
                    break
                else:
                    temp_C_volume = int(str(last_data.loc[last_index,'Volume(C)']).replace(',',''))
                #normalize volume
                if temp_c_vol_max == 0:
                    inputs.append(0)        
                else:
                    inputs.append(temp_C_volume / abs(temp_c_vol_max))
               
                #get last settle
                if days == 0:
                    last_settle = last_data.loc[last_index,'Settle(C)']
    
                days = days + 1
                temp_date = u_time          
                
            if len(inputs) == (dim*2):           
                Predict_data.update({code+'_C_'+str(last_settle):inputs})      
                    
        #for put options one day
        for i in range(len(data)):
            code = data.loc[i,'Option Code']
            if data.loc[i,'Change(P%)'] == '-':
                continue
            if data.loc[i,'Change(HSIo,P%)'] == '-':
                continue
    
            inputs = []   
            days = 0
            temp_date = begin
            while(days < dim):
                #search previous trading day
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
                while((not os.path.exists('../option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                u_time = last_date[0:10]
                last_data = pd.read_csv('../option_data/option_' + u_time + '.csv')
                #get max change value at that day
                changes_p = last_data['Change(P%)'].tolist()
                while '-' in changes_p:
                    changes_p.remove('-')
                temp_changes_p_max = max([float(cp) for cp in changes_p])
                temp_changes_p_min = min([float(cp) for cp in changes_p])
                #get change value for one option at that day
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                if last_data.loc[last_index,'Change(P%)'] == '-':
                    break
                else:
                    temp_P_change = float(last_data.loc[last_index,'Change(P%)'])
                #normalize change value and store
                if temp_changes_p_max == 0:
                    p_scale = abs(temp_changes_p_min)
                    inputs.append(temp_P_change / p_scale)       
                elif temp_changes_p_min == 0:
                    p_scale = abs(temp_changes_p_max)
                    inputs.append(temp_P_change / p_scale) 
                else:
                    if temp_P_change >= 0:
                        p_scale = abs(temp_changes_p_max)
                    else:
                        p_scale = abs(temp_changes_p_min)
                    inputs.append(temp_P_change / p_scale) 
                
                #get max volume at that day
                volumes_p = last_data['Volume(P)'].tolist()
                while '-' in volumes_p:
                    volumes_p.remove('-')
                temp_p_vol_max = max([int(str(vp).replace(',','')) for vp in volumes_p])
                #get volume for above option at that day
                if last_data.loc[last_index,'Volume(P)'] == '-':
                    break
                else:
                    temp_P_volume = int(str(last_data.loc[last_index,'Volume(P)']).replace(',',''))
                #normalize volume
                if temp_p_vol_max == 0:
                    inputs.append(0)        
                else:
                    inputs.append(temp_P_volume / abs(temp_p_vol_max))
                    
                if days == 0:
                    last_settle = last_data.loc[last_index,'Settle(P)']
    
                days = days + 1
                temp_date = u_time
                
            if len(inputs) == (dim*2):          
                Predict_data.update({code+'_P_'+str(last_settle):inputs})
            
        if Predict_data:
            Predict_data_pd = pd.DataFrame.from_dict(Predict_data, orient='index').T
            file_name = '../predict_data/' + 'predict_data_' + str(dim) + 'd_' + begin
            Predict_data_pd.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
    
        #search next trading day
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        while((not os.path.exists('../option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10] <= '2018-12-31'):
            count = count + 1
            next_date = str(begin_date + timedelta(days = count))
        begin = next_date[0:10]
        
    return 0

begin_ends_5 = [
            ['2018-01-08','2018-01-31'],
            ['2018-02-07','2018-02-28'],
            ['2018-03-07','2018-03-29'],
            ['2018-04-10','2018-04-30'],
            ['2018-05-08','2018-05-31'],
            ['2018-06-07','2018-06-29'],
            ['2018-07-09','2018-07-31'],
            ['2018-08-07','2018-08-31'],
            ['2018-09-07','2018-09-28'],
            ['2018-10-08','2018-10-31'],
            ['2018-11-07','2018-11-30'],
            ['2018-12-07','2018-12-31'],
            ]

begin_ends_10 = [
            ['2018-01-15','2018-01-31'],
            ['2018-02-14','2018-02-28'],
            ['2018-03-14','2018-03-29'],
            ['2018-04-17','2018-04-30'],
            ['2018-05-15','2018-05-31'],
            ['2018-06-14','2018-06-29'],
            ['2018-07-16','2018-07-31'],
            ['2018-08-14','2018-08-31'],
            ['2018-09-14','2018-09-28'],
            ['2018-10-15','2018-10-31'],
            ['2018-11-14','2018-11-30'],
            ['2018-12-14','2018-12-31'],
            ] 

dim = 10 #feature dim

for i in range(len(begin_ends_10)):
    PredictData(begin_ends_10[i][0], begin_ends_10[i][1], dim)
    
   
    
    
    
    
    
    
