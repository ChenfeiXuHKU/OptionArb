from __future__ import division
import pandas as pd
import numpy as np
from datetime import datetime 
from datetime import timedelta
import os
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb\utils")
import utils as ut

def StatArb(begin, end, number, option_info):
        	
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
        portfolio = searchPortfolio(begin, number)

        current_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(current_date + timedelta(days = count))
        while((not os.path.exists('../option_data/arb_data_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-12-31'):
            count = count + 1
            next_date = str(current_date + timedelta(days = count))   
        arb_data = pd.read_csv('../option_data/arb_data_' + next_date[0:10] + '.csv')        
        
        #daily stats
        fund = 0
        long_fund = 0
        short_fund = 0
        
        pnl = 0
        long_pnl = 0 
        short_pnl = 0

        long_fee = 0
        short_fee = 0
        print(begin)
        print(portfolio)
        print('---------------------------------')
        
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
                
            last_long_settle = portfolio['1'][2][i]
            last_short_settle = portfolio['-1'][2][i]                   
            
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
                
                if long_open <= 1.1*last_long_settle:
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
                
                if short_open >= 0.9*last_short_settle: 
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
        short_money_cum = short_money_cum + short_pnl
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


def searchPortfolio(begin, number):        
        
    call_data = pd.read_csv('../option_data/option_' + begin + '.csv')
    put_data = pd.read_csv('../option_data/option_' + begin + '.csv')
    data = call_data.append(put_data, ignore_index=True)
    portfolio = {}
            
    longs = [] 
    shorts = []
    long_settles = []
    short_settles = []
    long_types = []
    short_types = []
            
    settle_c = np.array(call_data['Settle(C)'].tolist())
#    t_p_c =  np.array(call_data['T-Price(tree,C)'].tolist())
    settle_p = np.array(put_data['Settle(P)'].tolist())
#    t_p_p =  np.array(put_data['T-Price(tree,P)'].tolist())
    t_p_c =  np.array(call_data['T-Price(BS,C)'].tolist())
    t_p_p =  np.array(put_data['T-Price(BS,P)'].tolist())
    
    diff_c = settle_c - t_p_c
    diff_p = settle_p - t_p_p
    diff= np.append(diff_c, diff_p)
    border = len(diff)/2
    sort_index = np.argsort(diff).tolist()
    l=0
    s=0
        #分位数去极值
    up = pd.DataFrame(diff).quantile([0.01,0.99]).iloc[1,:].tolist()[0]
    down = pd.DataFrame(diff).quantile([0.01,0.99]).iloc[0,:].tolist()[0]
    for k in range(len(sort_index)):
        if diff[sort_index[k]]>= down:
            l = k
            break
    for k in range(len(sort_index)):
        if diff[sort_index[k]]<= up:
            s = k
    s = len(sort_index) - s - 1
    long_index = sort_index[l:number+l]
    if s == 0:
        short_index = sort_index[-number-s:]
    else:
        short_index = sort_index[-number-s:-s]
            
    for i in range(number):
        if long_index[i] < border:# long calls
            longs.append(data.loc[long_index[i],'Option Code'])
            long_settles.append(float(data.loc[long_index[i],'Settle(C)']))
            long_types.append('C')
        else:# long puts
            longs.append(data.loc[long_index[i],'Option Code'])
            long_settles.append(float(data.loc[long_index[i],'Settle(P)']))
            long_types.append('P')
                
        if short_index[i] < border:
            shorts.append(data.loc[short_index[i],'Option Code'])
            short_settles.append(float(data.loc[short_index[i],'Settle(C)']))
            short_types.append('C')
        else:
            shorts.append(data.loc[short_index[i],'Option Code'])
            short_settles.append(float(data.loc[short_index[i],'Settle(P)']))
            short_types.append('P')
                
    portfolio['1'] = [longs, long_types, long_settles]
    portfolio['-1'] = [shorts, short_types, short_settles]
    
    return portfolio


#%%
option_info=pd.read_excel('../option_info.xlsx') 

begin_ends = [
            ['2017-12-29','2018-01-29'],
            ['2018-01-31','2018-02-26'],
            ['2018-02-28','2018-03-27'],
            ['2018-03-29','2018-04-26'],
            ['2018-04-30','2018-05-29'],
            ['2018-05-31','2018-06-27'],
            ['2018-06-29','2018-07-27'],
            ['2018-07-31','2018-08-29'],
            ['2018-08-31','2018-09-26'],
            ['2018-09-28','2018-10-29'],
            ['2018-10-31','2018-11-28'],
            ['2018-11-30','2018-12-27'],
            ]

names = ['2017-12','2018-01','2018-02','2018-03',\
         '2018-04','2018-05','2018-06','2018-07',\
         '2018-08','2018-09','2018-10','2018-11',]

option_info=pd.read_excel('../option_info.xlsx') 
numbers = [15] #choose how many options

for number in numbers:
    all_Return = []
    all_Long_Return = []
    all_Short_Return = []
    all_Period = []
    all_fund_cum = []
    all_long_fund_cum = []
    all_short_fund_cum = []    
    
    for i in range(len(begin_ends)):
        
        temp_Period,temp_fund_cum,temp_Return,temp_long_fund_cum,temp_Long_Return,\
            temp_short_fund_cum,temp_Short_Return = StatArb(begin_ends[i][0], begin_ends[i][1], number, option_info)
        
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
    
    print(indis.T)
    
    name='Results('+str(number)+'options, BS)'
    wbw = pd.ExcelWriter(name+'.xlsx')
    indis.to_excel(wbw, 'Indicators')
    data.to_excel(wbw, 'PnL')
    
    
    wbw.save()
    wbw.close()



