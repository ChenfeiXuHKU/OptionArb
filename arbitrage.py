from __future__ import division
import pandas as pd
import numpy as np
from datetime import datetime 
from datetime import timedelta
import os

def Calcuate_performance_indicators(return_data, period=252):
    #总收益
    Total_return=(return_data+1).cumprod(axis=0)[-1]-1
    #平均日收益
    Average_return = return_data.mean()
    #年化收益
    Annualized_Return = (return_data+1).cumprod(axis=0)[-1]**(365/len(return_data))-1
    #年化波动率：如果用月收益,年化应该乘以12的平方根
    Annualized_Volatility = return_data.std(axis=0)*period**0.5
    #年化夏普比
    Sharp = Annualized_Return/Annualized_Volatility
    #年化sortino比率
    down_return_data = []
    for r in return_data:
        if r < 0:
            down_return_data.append(r)
    Annualized_Down_Volatility = np.array(down_return_data).std(axis=0)*period**0.5
    Sortino = Annualized_Return/Annualized_Down_Volatility
    #最大回撤
    Maxdrawndown=[]
    l=[]
    for j in range(len(return_data)):
        l.append(((return_data+1).cumprod(axis=0)[j]-(return_data+1).cumprod(axis=0)[:j].max())/(return_data+1).cumprod(axis=0)[:j].max())
    Maxdrawndown.append(np.nanmin(np.array(l)));

    indis = [Total_return,Average_return,Annualized_Return,Annualized_Volatility,Sharp,Maxdrawndown[0],Sortino]

    df = pd.DataFrame(index = ['Tree Method'], columns=['Total Return','Average Return','Annualized Return',\
                      'Annualized Vol','Sharpe','Max Drawdown','Sortino','Calmar','胜率','盈亏比','最大盈利','最大亏损'])
    df['Total Return']=indis[0]
    df['Average Return']=indis[1]
    df['Annualized Return']=indis[2]
    df['Annualized Vol']=indis[3]
    df['Sharpe']=indis[4]
    df['Max Drawdown']=indis[5]
    df['Sortino']=indis[6]
    
    df["Calmar"] =  -df['Annualized Return']/df['Max Drawdown']
    df["胜率"] = sum(np.where(return_data > 0, 1, 0)) /sum(np.where(return_data == 0, 0, 1))
    df["盈亏比"] = -np.nanmean(return_data[return_data>0])/np.nanmean(return_data[return_data<0])
    df["最大盈利"] = return_data.max()
    df["最大亏损"] = return_data.min()
   
    return(df)

#%%
def arbitrage(begin, end, number, option_info, fund):
	
    PnL = []
    Return = []
#    PnL_cum_fees = []
    Period = []
    fund_cum = []
    #skip expiry dates
    special_list = ['2018-04-27', '2018-05-30', '2018-06-28', '2018-07-30']

    while begin != end:

        if begin not in special_list:
#%%
            data = pd.read_csv('option_data/option_' + begin + '.csv')

            call_portfolio = {}
            
            long_calls = [] 
            short_calls = []
            long_c_strikes = []
            short_c_strikes = []
            long_c_settles = []
            short_c_settles = []
            
            settle_c = np.array(data['Settle(C)'].tolist())
            t_p_c =  np.array(data['T-Price(tree,C)'].tolist())
            #t_p_c =  np.array(data['T-Price(BS,C)'].tolist())
            diff = settle_c - t_p_c
            sort_index = np.argsort(diff).tolist()
            l=0
            s=0
            
            #3sigma去极值
#            mu = np.mean(diff)
#            sigma = np.std(diff)
#            up = mu + 3*sigma
#            down = mu - 3*sigma

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
            
            long_call_index = sort_index[l:number+l]
            if s == 0:
                short_call_index = sort_index[-number-s:]
            else:
                short_call_index = sort_index[-number-s:-s]
                
#            print(str(l)+","+str(s))
#            print(str(long_call_index)+","+str(short_call_index))
            #construct call portfolio
            for i in range(number):
                long_calls.append(data.loc[long_call_index[i],'Option Code'])
                long_c_strikes.append(float(data.loc[long_call_index[i],'Strike']))
                long_c_settles.append(float(data.loc[long_call_index[i],'Settle(C)']))
                short_calls.append(data.loc[short_call_index[i],'Option Code'])
                short_c_strikes.append(float(data.loc[short_call_index[i],'Strike']))
                short_c_settles.append(float(data.loc[short_call_index[i],'Settle(C)']))
                
            call_portfolio['1'] = [long_calls, long_c_strikes, long_c_settles]
            call_portfolio['-1'] = [short_calls, short_c_strikes, short_c_settles]
             
#%% arb
            current_date = datetime.strptime(begin,'%Y-%m-%d')
            count = 1
            next_date = str(current_date + timedelta(days = count))
            while((not os.path.exists('option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-10-01'):
                count = count + 1
                next_date = str(current_date + timedelta(days = count))
            
            arb_data = pd.read_csv('option_data/arb_data_' + next_date[0:10] + '.csv')
            
            long_fund = 0
            short_fund = 0
            long_pnl = 0 
            short_pnl = 0
            pnl = 0
            long_fee = 0
            short_fee = 0

            for i in range(number):
                
                print(next_date[0:10]+':'+str(i)+':') 
                
                long_index = arb_data[(arb_data['Option Code'] == call_portfolio['1'][0][i])].index.tolist()[0]   			 
                short_index = arb_data[(arb_data['Option Code'] == call_portfolio['-1'][0][i])].index.tolist()[0]
                
                #long_c_settle, long_c_open = arb_data.loc[long_info,'Settle(C)'],arb_data.loc[long_info,'Open(C)']
                #short_c_settle, short_c_open = arb_data.loc[short_info,'Settle(C)'],arb_data.loc[short_info,'Open(C)']
                
                long_c_settle, long_c_open = arb_data.loc[long_index,'Settle(C)'],arb_data.loc[long_index,'Open(C)']
                short_c_settle, short_c_open = arb_data.loc[short_index,'Settle(C)'],arb_data.loc[short_index,'Open(C)']
                
                print(call_portfolio['1'][0][i] + ',s:' + str(long_c_settle)+ ',o:'+str(long_c_open))
                print(call_portfolio['-1'][0][i] + ',s:' + str(short_c_settle) + ',o:' + str(short_c_open))
                
                long_info = option_info[(option_info['Option Code'] == call_portfolio['1'][0][i])].index.tolist()[0]   			 
                short_info = option_info[(option_info['Option Code'] == call_portfolio['-1'][0][i])].index.tolist()[0]
                 
                #buy side
                if long_c_open > 0 and long_c_settle > 0:
                    if option_info.loc[long_info,'Tier']==1:
                        long_fee = long_fee + 3
                    elif option_info.loc[long_info,'Tier']==2:
                        long_fee = long_fee + 1
                    elif option_info.loc[long_info,'Tier']==3:
                        long_fee = long_fee + 0.5
                        
                    long_fund = long_fund + long_c_open*option_info.loc[long_info,'Contract Size'] + long_fee
                    long_pnl = long_pnl + (long_c_settle - long_c_open)*option_info.loc[long_info,'Contract Size'] - long_fee
                
                #short side
                if short_c_open > 0 and short_c_settle > 0:
                    if option_info.loc[short_info,'Tier']==1:
                        short_fee = short_fee + 3
                    elif option_info.loc[short_info,'Tier']==2:
                        short_fee = short_fee + 1
                    elif option_info.loc[short_info,'Tier']==3:
                        short_fee = short_fee + 0.5
                        
                    short_fund = short_fund + short_c_open*option_info.loc[short_info,'Contract Size'] + short_fee
                    short_pnl = short_pnl - (short_c_settle - short_c_open)*option_info.loc[short_info,'Contract Size'] - short_fee
                
                if short_fund>0:
                    print('short size:'+str(option_info.loc[short_info,'Contract Size']))
                    print('short fund:'+str(short_fund))
                if long_fund>0:
                    print('long size:'+str(option_info.loc[long_info,'Contract Size']))
                    print('long fund:'+str(long_fund))
                #print('pnl:'+str(long_pnl+short_pnl))


            if long_fund > 0 and short_fund > 0:
                #hands_portfolio_long =  int(l_fund/long_fund)
                #hands_portfolio_short = int(s_fund/short_fund)
                #pnl = long_pnl*hands_portfolio_long +short_pnl*hands_portfolio_short
                pnl = long_pnl+short_pnl
                #print('long hands:'+str(hands_portfolio_long))
                #print('short hands:'+str(hands_portfolio_short))
                print('pnl:'+str(pnl))
                
            elif long_fund == 0 and short_fund > 0:
                #hands_portfolio_short = int(s_fund/short_fund)
                #pnl = short_pnl*hands_portfolio_short
                pnl = short_pnl
                #print('short hands:'+str(hands_portfolio_short))
                print('pnl:'+str(pnl))
                
            elif short_fund == 0 and long_fund > 0:
                #hands_portfolio_long = int(l_fund/long_fund)
                #pnl = long_pnl*hands_portfolio_long
                pnl = long_pnl
                #print('long hands:'+str(hands_portfolio_long))
                print('pnl:'+str(pnl))
            
            print('---------------------------------')    
            Return.append(pnl/fund)
            PnL.append(round(pnl,2))
            fund = fund + pnl
            fund_cum.append(round(fund,2))
            Period.append(next_date[0:10])
            
            begin = next_date[0:10]

        else:
            count = 1
            current_date = datetime.strptime(begin,'%Y-%m-%d')
            next_date = str(current_date + timedelta(days = count))
            while((not os.path.exists('option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-10-01'):
                count = count + 1
                next_date = str(current_date + timedelta(days = count))
            begin = next_date[0:10]

    return PnL,fund_cum,Return,Period


option_info=pd.read_excel('option_info.xlsx') 

begin = '2018-05-02'
end = '2018-07-31'

fund = 10000

PnL,fund_cum,Return,Period = arbitrage(begin, end, 1, option_info, fund)


data = pd.DataFrame(index = Period, columns=['PnL','PnL_cum','Fund_cum','Return'])
data['PnL']=np.array(PnL)
data['PnL_cum']=np.array(PnL)
data['PnL_cum']=data['PnL_cum'].cumsum(axis=0)
data['Fund_cum']=np.array(fund_cum)
data['Return']=np.array(Return)

indicators = Calcuate_performance_indicators(data['Return'], 252)

#print(sum(PnL))
print(indicators.T)
#data['PnL_cum_fees']=np.array(PnL_cum_fees)

name='回测结果33'
wbw = pd.ExcelWriter(name+'.xlsx')
data.to_excel(wbw, 'PnL')
indicators.to_excel(wbw, 'Indicators')

    
wbw.save()
wbw.close()










