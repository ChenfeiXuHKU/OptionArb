# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 15:12:51 2018

@author: chenf
"""
import numpy as np
import pandas as pd

def sigmoid(z):

    s = 1/(1 + 1/np.exp(z))

    return s

def relu(z):
    
    s = np.maximum(z, 0)
    
    return s

def Calcuate_performance_indicators(return_data, period, type_s):
    #总收益
    Total_return=(return_data+1).cumprod(axis=0)[-1]-1
    #平均日收益
    Average_return = return_data.mean()
    #年化收益
    Annualized_Return = ((return_data+1).cumprod(axis=0)[-1]**(365/len(return_data)))-1
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

    df = pd.DataFrame(index = [type_s], columns=['TotalReturn','AverageReturn','AnnualizedReturn',\
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
