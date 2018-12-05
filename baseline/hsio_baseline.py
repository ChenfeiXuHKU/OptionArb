from __future__ import division
import pandas as pd
import numpy as np

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

    df = pd.DataFrame(index = ['HSI'], columns=['TotalReturn','AverageReturn','AnnualizedReturn',\
                      'AnnualizedVol','Sharpe','MaxDrawdown','Sortino','Calmar','WinRate','P/L Ratio','MaxProfit','MaxLoss'])
    df['TotalReturn']=indis[0]
    df['AverageReturn']=indis[1]
    df['AnnualizedReturn']=indis[2]
    df['AnnualizedVol']=indis[3]
    df['Sharpe']=indis[4]
    df['MaxDrawdown']=indis[5]
    df['Sortino']=indis[6]
    
    df["Calmar"] =  -df['AnnualizedReturn']/df['MaxDrawdown']
    df["WinRate"] = sum(np.where(return_data > 0, 1, 0)) /sum(np.where(return_data == 0, 0, 1))
    df["P/L Ratio"] = -np.nanmean(return_data[return_data>0])/np.nanmean(return_data[return_data<0])
    df["MaxProfit"] = return_data.max()
    df["MaxLoss"] = return_data.min()
   
    return(df)

#%%
def arbitrage():
	
    Return = []
    Period = []

    #skip expiry dates
    special_list = ['2018-04-27', '2018-05-30', '2018-06-28', '2018-07-30']
    
    data = pd.read_csv('./hsio_data/hsio.csv')
    
    for i in range(len(data)-1):
        
        date = data.loc[i,'Date']
        
        if date not in special_list:

            price_1 = data.loc[i,'HSI Price']
            price_2 = data.loc[i+1,'HSI Price']
            
            Return.append((price_2-price_1)/price_1)
            Period.append(data.loc[i+1,'Date'])

        else:
            continue

    return Return,Period

Return,Period = arbitrage()

data = pd.DataFrame(index = Period, columns=['Return'])
data['Return']=np.array(Return)

indicators = Calcuate_performance_indicators(data['Return'], 252)

print(indicators.T)

name='Results(HSI)'
wbw = pd.ExcelWriter(name+'.xlsx')
data.to_excel(wbw, 'PnL')
indicators.to_excel(wbw, 'Indicators')

    
wbw.save()
wbw.close()











