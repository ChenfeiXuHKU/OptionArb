from __future__ import division
import pandas as pd
import numpy as np
from datetime import datetime 
from datetime import timedelta
import os
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb")
import utils as ut

def StatArb(begin, end, number, option_info, fund, Long_fund, Short_fund):
        	
    Return = []
    Long_Return = []
    Short_Return = []
    Period = []
    fund_cum = []
    long_fund_cum = []
    short_fund_cum = []
    
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
        long_fund = 0
        short_fund = 0
        long_pnl = 0 
        short_pnl = 0
        pnl = 0
        long_fee = 0
        short_fee = 0
            
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
            
#            if short_fund>0:
#                print('short size:'+str(option_info.loc[short_info,'Contract Size']))
#                print('short fund:'+str(short_fund))
#            if long_fund>0:
#                print('long size:'+str(option_info.loc[long_info,'Contract Size']))
#                print('long fund:'+str(long_fund))

        if long_fund > 0 and short_fund > 0:
#                hands_portfolio_long =  int(l_fund/long_fund)
#                hands_portfolio_short = int(s_fund/short_fund)
#                pnl = long_pnl*hands_portfolio_long +short_pnl*hands_portfolio_short
            pnl = long_pnl+short_pnl
#                print('long hands:'+str(hands_portfolio_long))
#                print('short hands:'+str(hands_portfolio_short))
#            print('pnl:'+str(pnl))
                
        elif long_fund == 0 and short_fund > 0:
#                hands_portfolio_short = int(s_fund/short_fund)
#                pnl = short_pnl*hands_portfolio_short
            pnl = short_pnl
#                print('short hands:'+str(hands_portfolio_short))
#            print('pnl:'+str(pnl))
                
        elif short_fund == 0 and long_fund > 0:
#                hands_portfolio_long = int(l_fund/long_fund)
#                pnl = long_pnl*hands_portfolio_long
            pnl = long_pnl
#                print('long hands:'+str(hands_portfolio_long))
#            print('pnl:'+str(pnl))
            
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

        Period.append(next_date[0:10])
        begin = next_date[0:10]

    return Period,fund_cum,Return,long_fund_cum,Long_Return,short_fund_cum,Short_Return


def searchPortfolio(begin, number):        
        
    call_data = pd.read_csv('../option_data/option_' + begin + '.csv')
    put_data = pd.read_csv('../option_data/option_' + begin + '.csv')
    data = call_data.append(put_data, ignore_index=True)
    portfolio = {}
            
    longs = [] 
    shorts = []
    long_strikes = []
    short_strikes = []
    long_settles = []
    short_settles = []
    long_types = []
    short_types = []
            
    settle_c = np.array(call_data['Settle(C)'].tolist())
    t_p_c =  np.array(call_data['T-Price(tree,C)'].tolist())
    settle_p = np.array(put_data['Settle(P)'].tolist())
    t_p_p =  np.array(put_data['T-Price(tree,P)'].tolist())
        #t_p_c =  np.array(data['T-Price(BS,C)'].tolist())
        
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
            long_strikes.append(float(data.loc[long_index[i],'Strike']))
            long_settles.append(float(data.loc[long_index[i],'Settle(C)']))
            long_types.append('C')
        else:# long puts
            longs.append(data.loc[long_index[i],'Option Code'])
            long_strikes.append(float(data.loc[long_index[i],'Strike']))
            long_settles.append(float(data.loc[long_index[i],'Settle(P)']))
            long_types.append('P')
                
        if short_index[i] < border:
            shorts.append(data.loc[short_index[i],'Option Code'])
            short_strikes.append(float(data.loc[short_index[i],'Strike']))
            short_settles.append(float(data.loc[short_index[i],'Settle(C)']))
            short_types.append('C')
        else:
            shorts.append(data.loc[short_index[i],'Option Code'])
            short_strikes.append(float(data.loc[short_index[i],'Strike']))
            short_settles.append(float(data.loc[short_index[i],'Settle(P)']))
            short_types.append('P')
                
    portfolio['1'] = [longs, long_types, long_strikes, long_settles]
    portfolio['-1'] = [shorts, short_types, short_strikes, short_settles]
    
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
Fund = 100000
Long_fund = 100000
Short_fund = 100000
number = 20 #choose how many options

all_Return = []
all_Long_Return = []
all_Short_Return = []
all_Period = []
all_fund_cum = []
all_long_fund_cum = []
all_short_fund_cum = []

for i in range(len(begin_ends)):
    temp_Period,temp_fund_cum,temp_Return,temp_long_fund_cum,temp_Long_Return,\
    temp_short_fund_cum,temp_Short_Return = StatArb(begin_ends[i][0], begin_ends[i][1],\
                                                    number, option_info, Fund, Long_fund, Short_fund)

    Fund = temp_fund_cum[-1]
    Long_fund = temp_long_fund_cum[-1]
    Short_fund = temp_short_fund_cum[-1]
    
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

indicators = ut.Calcuate_performance_indicators(data['Return'], 252, 'Long-Short')
indicators_long = ut.Calcuate_performance_indicators(data['LongReturn'], 252, 'Long')
indicators_short = ut.Calcuate_performance_indicators(data['ShortReturn'], 252, 'Short')

indis = (indicators.append(indicators_long)).append(indicators_short)

print(indicators.T)

name='Results('+str(number)+'options, BinomialTree)'
wbw = pd.ExcelWriter(name+'.xlsx')
data.to_excel(wbw, 'PnL')
indis.to_excel(wbw, 'Indicators')

wbw.save()
wbw.close()




