# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 13:49:55 2019

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
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb\utils")
import utils as ut
import nn_modules as nnm

def Predict(begin, end, dim, number, parameters, activation, option_info):

    Period = []
    
    Return = []
    Long_Return = []
    Short_Return = []

    Money_Cum = []
    Long_Money_Cum = []
    Short_Money_Cum = []
    
    money_cum = 0
    long_money_cum = 0
    short_money_cum = 0
        
    while begin != end:
        
        portfolio = SearchPortfolio(begin, dim, number, parameters, activation)
        
#        daily stats
#        fund = 0
        long_fund = 0
        short_fund = 0
        
        pnl = 0
        long_pnl = 0 
        short_pnl = 0

        long_fee = 0
        short_fee = 0
        
        #begin backtesting
        arb_data = pd.read_csv('../option_data/arb_data_' + begin + '.csv')
        print(begin)
        print(portfolio)
        
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
                long_pnl = long_pnl + (long_settle - long_open)*option_info.loc[long_info,'Contract Size'] - 2*long_fee
                
            #short side
            if short_open > 0 and short_settle > 0:
                if option_info.loc[short_info,'Tier']==1:
                    short_fee = 3
                elif option_info.loc[short_info,'Tier']==2:
                    short_fee = 1
                elif option_info.loc[short_info,'Tier']==3:
                    short_fee = 0.5        
                    
                short_fund = short_fund + short_open*option_info.loc[short_info,'Contract Size'] + short_fee
                short_pnl = short_pnl - (short_settle - short_open)*option_info.loc[short_info,'Contract Size'] - 2*short_fee
        
        #long-short performance
        fund = long_fund + short_fund
        pnl = long_pnl + short_pnl
        if fund != 0:
            Return.append(pnl/fund)
        else:
            Return.append(0)
        money_cum = money_cum + pnl
        Money_Cum.append(round(money_cum,2))
        
        #long side performance
        if long_fund > 0:
            Long_Return.append(long_pnl/long_fund)
        else:
            Long_Return.append(0)     
        long_money_cum = long_money_cum + long_pnl
        Long_Money_Cum.append(round(long_money_cum,2))
                
        #short side performance
        if short_fund > 0:
            Short_Return.append(short_pnl/short_fund)
        else:
            Short_Return.append(0)
        short_money_cum = short_money_cum + long_pnl
        Short_Money_Cum.append(round(short_money_cum,2))
    
        Period.append(begin)
        
        #search next trading day
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        while((not os.path.exists('../option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10] <= '2018-12-31'):
            count = count + 1
            next_date = str(begin_date + timedelta(days = count))
        begin = next_date[0:10]
        
    return Period,Money_Cum,Return,Long_Money_Cum,Long_Return,Short_Money_Cum,Short_Return              
                
#%%
def SearchPortfolio(begin, dim, number, parameters, activation):
    
    portfolio = {}
    Predict_data = OrderedDict() 
    data = pd.read_csv('../predict_data/predict_data_' + str(dim) + 'd_' + begin + '.csv')
    
    #predict probs
    for i in range(data.shape[1]):
        x = data.iloc[:,i].values
        AL, caches = nnm.L_model_forward(x.reshape(x.shape[0],1), parameters, activation)
        Predict_data.update({data.columns[i]:AL[0][0]})      

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
            short_settles.append(float(ks[short_index[i]].split('_')[2]))
            longs.append(ks[long_index[i]].split('_')[0])
            long_types.append(ks[long_index[i]].split('_')[1])
            long_settles.append(float(ks[long_index[i]].split('_')[2]))
            
        portfolio['1'] = [longs, long_types, long_settles]
        portfolio['-1'] = [shorts, short_types, short_settles]

    return portfolio

#%%
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

names = ['2017-12','2018-01','2018-02','2018-03',\
         '2018-04','2018-05','2018-06','2018-07',\
         '2018-08','2018-09','2018-10','2018-11',]

option_info=pd.read_excel('../option_info.xlsx') 

dim = 5 #feature dim

num_iters = [1000,2000,3000]
num_lrs = [0.001,0.01,0.1]
activations = ['relu']
Ls = [3,]

option_number = 1 #choose how many options
layers_dims = [dim*2, dim, 3, 1]

for L in Ls: 
    for num_iter in num_iters:    
        for num_lr in num_lrs:   
            for activation in activations:
                        
                all_Return = []
                all_Long_Return = []
                all_Short_Return = []
                all_Period = []
                all_fund_cum = []
                all_long_fund_cum = []
                all_short_fund_cum = []
                
                for i in range(len(begin_ends_5)):
                    parameters = {}
                    for l in range(1, L+1):
                        
                        temp_w = np.loadtxt('./weights/w_' + str(L) + 'l_' + str(l) + '_' + str(num_lr) + \
                                  '_' + activation + '_' + str(num_iter) + '_' + names[i] + '.txt')
                        parameters['W' + str(l)] = temp_w.reshape(layers_dims[l],layers_dims[l-1])
                        temp_b = np.loadtxt('./weights/b_' + str(L) + 'l_' + str(l) + '_' + str(num_lr) + \
                                  '_' + activation + '_' + str(num_iter) + '_' + names[i] + '.txt')
                        parameters['b' + str(l)] = temp_b.reshape(layers_dims[l],1)

                    temp_Period,temp_fund_cum,temp_Return,temp_long_fund_cum,temp_Long_Return,\
                            temp_short_fund_cum,temp_Short_Return = Predict(begin_ends_5[i][0], begin_ends_5[i][1], \
                                                                            dim, option_number, parameters, activation, option_info)
                    all_Return = all_Return + temp_Return
                    all_Long_Return = all_Long_Return + temp_Long_Return
                    all_Short_Return = all_Short_Return + temp_Short_Return
                    all_Period = all_Period + temp_Period
                    all_fund_cum = all_fund_cum + temp_fund_cum
                    all_long_fund_cum = all_long_fund_cum + temp_long_fund_cum
                    all_short_fund_cum = all_short_fund_cum + temp_short_fund_cum
                        
                data = pd.DataFrame(index = all_Period, columns=['FundCum','Return','LongFundCum','LongReturn','ShortFundCum','ShortReturn'])
                data['FundCum']=np.array(all_fund_cum)
                data['Return']=np.array(all_Return)
                data['LongFundCum']=np.array(all_long_fund_cum)
                data['LongReturn']=np.array(all_Long_Return)
                data['ShortFundCum']=np.array(all_short_fund_cum)
                data['ShortReturn']=np.array(all_Short_Return)
                        
                indicators = ut.Calcuate_performance_indicators(data['Return'], 244, 'Long-Short')   
                indicators_long = ut.Calcuate_performance_indicators(data['LongReturn'], 244, 'Long')   
                indicators_short = ut.Calcuate_performance_indicators(data['ShortReturn'], 244, 'Short')
                        
                indis = (indicators.append(indicators_long)).append(indicators_short)
                        
                print(indicators.T)
                        
                name='./results/Results(' + str(L) + 'layers-'+str(option_number)+'options-'+str(num_lr) + \
                                  '-' + activation + '-' + str(num_iter)
                wbw = pd.ExcelWriter(name+'.xlsx')
                
                indis.to_excel(wbw, 'Indicators')
                data.to_excel(wbw, 'PnL')
                        
                wbw.save()
                wbw.close()            
