# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 19:57:41 2018

@author: chenf
"""
from __future__ import division
import pandas as pd
from datetime import datetime 
from collections import OrderedDict
from datetime import timedelta
import os
import numpy as np
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb")
import utils as ut

tid = 1
name = '2017-12'
w = np.loadtxt('w_' + name + '_' + str(tid) + '.txt')
b = np.loadtxt('b_' + name + '_' + str(tid) + '.txt')


def predict(begin, end, dim, number, w, b, option_info, fund):

    w = w.reshape(dim*2, 1)
    Return = []
    Long_Return = []
    Short_Return = []
    Period = []
    fund_cum = []
    long_fund_cum = []
    short_fund_cum = []
    Long_fund = fund
    Short_fund = fund
    
    while begin != end:
        SearchPortfolio(begin, dim, number, w, b)       
        
        #daily stats
        long_fund = 0
        short_fund = 0
        long_pnl = 0 
        short_pnl = 0
        pnl = 0
        long_fee = 0
        short_fee = 0
        
        #begin backtesting
        arb_data = pd.read_csv('../option_data/arb_data_' + begin + '.csv')
        
        #for each short-long pair
        for i in range(number):
            long_i = arb_data[(arb_data['Option Code'] == portfolio['1'][0][i])].index.tolist()[0]   			 
            short_i = arb_data[(arb_data['Option Code'] == portfolio['-1'][0][i])].index.tolist()[0]
                
            if portfolio['1'][1][i] == 'C' and portfolio['-1'][1][i] == 'C':
                long_settle, long_open = arb_data.loc[long_i,'Settle(C)'],arb_data.loc[long_i,'Open(C)']               
                short_settle, short_open = arb_data.loc[short_i,'Settle(C)'],arb_data.loc[short_i,'Open(C)']            
            elif portfolio['1'][1][i] == 'C' and portfolio['-1'][1][i] == 'P':
                long_settle, long_open = arb_data.loc[long_i,'Settle(C)'],arb_data.loc[long_i,'Open(C)']
                short_settle, short_open = arb_data.loc[short_i,'Settle(P)'],arb_data.loc[short_i,'Open(P)']                       
            elif portfolio['1'][1][i] == 'P' and portfolio['-1'][1][i] == 'C':
                long_settle, long_open = arb_data.loc[long_i,'Settle(P)'],arb_data.loc[long_i,'Open(P)']
                short_settle, short_open = arb_data.loc[short_i,'Settle(C)'],arb_data.loc[short_i,'Open(C)']                       
            elif portfolio['1'][1][i] == 'P' and portfolio['-1'][1][i] == 'P':
                long_settle, long_open = arb_data.loc[long_i,'Settle(P)'],arb_data.loc[long_i,'Open(P)']
                short_settle, short_open = arb_data.loc[short_i,'Settle(P)'],arb_data.loc[short_i,'Open(P)']
            
            #close2-close1 as need
#            last_long_settle = portfolio['1'][2][i]
#            last_short_settle = portfolio['-1'][2][i]
            
            long_info = option_info[(option_info['Option Code'] == portfolio['1'][0][i])].index.tolist()[0]   			 
            short_info = option_info[(option_info['Option Code'] == portfolio['-1'][0][i])].index.tolist()[0]        
                
            #buy side
            if long_open > 0 and long_settle > 0:
                if option_info.loc[long_info,'Tier']==1:
                    long_fee = 3
                elif option_info.loc[long_info,'Tier']==2:
                    long_fee = 1
                elif option_info.loc[long_info,'Tier']==3:
                    long_fee = 0.5       
                long_fund = long_fund + long_open*option_info.loc[long_info,'Contract Size'] + long_fee
#                long_fund = long_fund + last_long_settle*option_info.loc[long_info,'Contract Size'] + long_fee
                long_pnl = long_pnl + (long_settle - long_open)*option_info.loc[long_info,'Contract Size'] - 2*long_fee
#                long_pnl = long_pnl + (long_settle - last_long_settle)*option_info.loc[long_info,'Contract Size'] - 2*long_fee
    
            #short side
            if short_open > 0 and short_settle > 0:
                if option_info.loc[short_info,'Tier']==1:
                    short_fee = 3
                elif option_info.loc[short_info,'Tier']==2:
                    short_fee = 1
                elif option_info.loc[short_info,'Tier']==3:
                    short_fee = 0.5            
                short_fund = short_fund + short_open*option_info.loc[short_info,'Contract Size'] + short_fee
#                short_fund = short_fund + last_short_settle*option_info.loc[short_info,'Contract Size'] + short_fee
                short_pnl = short_pnl - (short_settle - short_open)*option_info.loc[short_info,'Contract Size'] - 2*short_fee
#                short_pnl = short_pnl - (short_settle - last_short_settle)*option_info.loc[short_info,'Contract Size'] - 2*short_fee
    
#            if short_fund>0:
#                print('short size:'+str(option_info.loc[short_info,'Contract Size']))
#                print('short fund:'+str(short_fund))
#            if long_fund>0:
#                print('long size:'+str(option_info.loc[long_info,'Contract Size']))
#                print('long fund:'+str(long_fund))
    
        if long_fund > 0 and short_fund > 0:
            pnl = long_pnl + short_pnl
        elif long_fund == 0 and short_fund > 0:
            pnl = short_pnl
        elif short_fund == 0 and long_fund > 0:
            pnl = long_pnl

        Return.append(pnl/fund)
        fund = fund + pnl
        fund_cum.append(round(fund,2))
    
        if long_fund > 0:
            Long_Return.append(long_pnl/Long_fund)
            Long_fund = Long_fund + long_pnl
            long_fund_cum.append(round(Long_fund,2))
        else:
            Long_Return.append(0)
            long_fund_cum.append(round(Long_fund,2))
                
        if short_fund > 0:
            Short_Return.append(short_pnl/Short_fund)
            Short_fund = Short_fund + short_pnl
            short_fund_cum.append(round(Short_fund,2))
        else:
            Short_Return.append(0)
            short_fund_cum.append(round(Short_fund,2))
    
        Period.append(begin)
        
        #search next trading day
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        while((not os.path.exists('../option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10] < '2018-12-28'):
            count = count + 1
            next_date = str(begin_date + timedelta(days = count))
        begin = next_date[0:10]
        
    return Period,fund_cum,Return,long_fund_cum,Long_Return,short_fund_cum,Short_Return              
                

def SearchPortfolio(begin, dim, number):
    portfolio = {}
    Predict_data = OrderedDict() 
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
            prob = ut.sigmoid(np.dot(w.T,np.array(inputs).reshape(dim*2,1)) + b)
            Predict_data.update({code+'_C_'+last_settle:prob})      
                
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
            prob = ut.sigmoid(np.dot(w.T,np.array(inputs).reshape(dim*2,1)) + b)
            Predict_data.update({code+'_P_'+last_settle:prob})
                
    #sort
    if Predict_data:
        longs = []
        shorts = []
        long_types = []
        short_types = []
        long_settles = []
        short_settles = []
            
        probs = list(Predict_data.values())
        ks = list(Predict_data.keys())
        sort_index = np.argsort(np.array(probs)).tolist()   
        short_index = sort_index[0:number]
        long_index = sort_index[-number:]
            
        for i in range(number):
            shorts.append(ks[short_index[i]].split('_')[0])
            short_types.append(ks[short_index[i]].split('_')[1])
            short_settles.append(float(ks[short_index[i]].split('_')[2])
            longs.append(ks[long_index[i]].split('_')[0])
            long_types.append(ks[long_index[i]].split('_')[1])
            long_settles.append(float(ks[long_index[i]].split('_')[2]))
            
        portfolio['1'] = [longs, long_types, long_settles]
        portfolio['-1'] = [shorts, short_types, short_settles]

    return portfolio



begin_ends_5 = [
            ['2018-01-08','2018-01-29'],
#            ['2018-02-07','2018-02-28'],
#            ['2018-03-07','2018-03-29'],
#            ['2018-04-10','2018-04-30'],
#            ['2018-05-08','2018-05-31'],
#            ['2018-06-07','2018-06-29'],
#            ['2018-07-09','2018-07-31'],
#            ['2018-08-07','2018-08-31'],
#            ['2018-09-07','2018-09-28'],
#            ['2018-10-08','2018-10-31'],
#            ['2018-11-07','2018-11-30'],
        ]
    
# for 10 features
begin_ends_10 = [
            ['2017-07-17','2017-07-31'],
            ['2017-08-14','2017-08-31'],
            ['2017-09-14','2017-10-03'],
            ['2017-10-18','2017-10-31'],
            ['2017-11-14','2017-11-30'],
            ['2017-12-14','2017-12-29'],
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
            ] 

option_info=pd.read_excel('../option_info.xlsx') 


for i in range(len(begin_ends_10)):
    month_data = get_data(begin_ends_10[i][0], begin_ends_10[i][1], 10)
        
    file_name = 'train_data' + '/train_data_10d_' + begin_ends_10[i][0][0:7]
    month_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)              
    

            
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                