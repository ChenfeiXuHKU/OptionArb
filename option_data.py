#http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options
from __future__ import division
from datetime import datetime 
from time import sleep
from collections import OrderedDict
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
import quandl
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'
from lxml import html  
import requests
    
#get hk option code and their underlying 
def get_code():
    url = "http://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Single-Stock/Stock-Options?sc_lang=en#&sttype=options"

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    response = webdriver.Chrome(options=chrome_options)
    response.get(url)
    sleep(10)
    response.find_element_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[1]/span').click()

    l = response.find_elements_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[2]/div')
    response.find_elements_by_xpath('//*[@id="lhkexw-singlestocklanding"]/section/div[2]/div/div[3]/div[2]/div[2]/div[{0}]/span'.format(len(l)))[0].click()

    code_list = response.find_elements_by_xpath('//*[@id="mCSB_1_container"]/div/div/table/tbody/tr')

    code=[]
    underlying=[]
    vol=[]
    
    for i in range(len(code_list)):
        c = code_list[i].find_elements_by_xpath('.//td[1]')[0].text
        u = code_list[i].find_elements_by_xpath('.//td[2]')[0].text
        v = code_list[i].find_elements_by_xpath('.//td[5]')[0].text

        if (i > 0) and (u == underlying[-1]):
            #print float(vol[i-1].replace(",", "")),code[i-1],underlying[i-1]
            if float(v.replace(",", "")) > float(vol[-1].replace(",", "")):
                del code[-1]
                del underlying[-1]
                del vol[-1]
                code.append(c)
                underlying.append(u)
                vol.append(v)
        else:
            code.append(c)
            underlying.append(u)
            vol.append(v)

    return code, underlying  


#get option trading info (at/near the money, 1 month)
def get_option(code, underlying, o_data, u_time, expiry, maturity, hsi_price):

    summary_data = OrderedDict()

    summary_data.update({'Date':u_time})
    summary_data.update({'Stock Code':underlying})
    summary_data.update({'Option Code':code})
    
    if len(underlying)<5:
            underlying = (5-len(underlying))*'0' + underlying

    u_d,net_change,change_per,price = get_BBands(underlying, u_time, 26)

    summary_data.update({'Closing':price})
    summary_data.update({'Change':net_change})
    summary_data.update({'Change(%)':change_per})
    
    url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio{0}.htm".format(u_time.replace("-", "")[2:])

    response = requests.get(url)
    s=response.text
    parser = html.fromstring(s)

    hsi_data = parser.xpath('/html/body/pre/text()')
    hsi_o = hsi_data[1].split('\n')
    
    diff_hsi_c = 9999
    diff_hsi_p = 9999
    #select at/near the money
    index_hsi_c = 0
    index_hsi_p = 0
    
    if len(hsi_o) > 0:
        for i in range(len(hsi_o)):
            w = hsi_o[i].split()
            if len(w) > 2 and w[2] == 'C':
                c = w[1]
                if abs(float(c) - hsi_price) < diff_hsi_c:
                    diff_hsi_c = abs(float(c) - hsi_price)
                    index_hsi_c = i
            elif len(w) > 2 and w[2] == 'P':
                p = w[1]
                if abs(float(p) - hsi_price) < diff_hsi_p:
                    diff_hsi_p = abs(float(p) - hsi_price)
                    index_hsi_p = i
            
    if index_hsi_c != 0 and index_hsi_p != 0:
        if len(hsi_o[index_hsi_c].split()) > 12:
            
            HSIStrike = hsi_o[index_hsi_c].split()[1]
            HSI_C = hsi_o[index_hsi_c].split()[12]
            HSI_C_C = hsi_o[index_hsi_c].split()[13]
            HSI_C_O = hsi_o[index_hsi_c].split()[9]
            
            HSI_P = hsi_o[index_hsi_p].split()[12]
            HSI_P_C = hsi_o[index_hsi_p].split()[13]
            HSI_P_O = hsi_o[index_hsi_p].split()[9]
        else:
            HSIStrike = hsi_o[index_hsi_c].split()[1]
            HSI_C = hsi_o[index_hsi_c].split()[6]
            HSI_C_C = hsi_o[index_hsi_c].split()[7]
            HSI_C_O = hsi_o[index_hsi_c].split()[3]
            
            HSI_P = hsi_o[index_hsi_p].split()[6]
            HSI_P_C = hsi_o[index_hsi_p].split()[7]
            HSI_P_O = hsi_o[index_hsi_p].split()[3]
        
        summary_data.update({'HSI Price':hsi_price})
        summary_data.update({'HSI Strike':float(HSIStrike)})
        summary_data.update({'Open(HSIo,C)':HSI_C_O})
        summary_data.update({'Settle(HSIo,C)':HSI_C})
        summary_data.update({'Change(HSIo,C%)':round(100*float(HSI_C_C)/(float(HSI_C)-float(HSI_C_C)),2)})
        summary_data.update({'Open(HSIo,P)':HSI_P_O})
        summary_data.update({'Settle(HSIo,P)':HSI_P})
        summary_data.update({'Change(HSIo,P%)':round(100*float(HSI_P_C)/(float(HSI_P)-float(HSI_P_C)),2)})
    
    diff_c = 9999
    diff_p = 9999
    #select at/near the money
    index_c = 0
    index_p = 0
        
    if price > 0:
        for i in range(len(o_data)):
            w = o_data[i].split()
            if len(w) == 12 and w[2] == 'C' and w[0] == expiry:
                c = w[1]
                if abs(float(c) - price) < diff_c:
                    diff_c = abs(float(c) - price)
                    index_c = i
            elif len(w) == 12 and w[2] == 'P' and w[0] == expiry:
                p = w[1]
                if abs(float(p) - price) < diff_p:
                    diff_p = abs(float(p) - price)
                    index_p = i

    if index_p != 0 and index_c != 0:
        
        s_vol = get_s_vol(underlying, u_time, 21)
        IV_1C = o_data[index_c].split()[8]
        IV_1P = o_data[index_p].split()[8]
        Strike = o_data[index_c].split()[1]
        Volume_1C = o_data[index_c].split()[9]
        Volume_1P = o_data[index_p].split()[9]
        
        summary_data.update({'Strike':Strike})

        S_C = o_data[index_c].split()[6]        
        S_C_C = o_data[index_c].split()[7]
        O_C = o_data[index_c].split()[3]

        S_P = o_data[index_p].split()[6]
        S_P_C = o_data[index_p].split()[7]
        O_P = o_data[index_p].split()[3]

        summary_data.update({'SV':round(s_vol,2)*100})
        summary_data.update({'IV(C)':IV_1C})
        summary_data.update({'IV(P)':IV_1P})
        summary_data.update({'Volume(C)':Volume_1C.replace(',', '')})
        summary_data.update({'Volume(P)':Volume_1P.replace(',', '')})

        r = 0.0015
        q = 0.0424
        Expiry = maturity
#        T = (Expiry - int(u_time[8:10].lstrip('0')))/365
        T = 28/365
        theo_c_BI = binomialTree(price, s_vol, r, T, float(Strike), 3, 'C')
        theo_p_BI = binomialTree(price, s_vol, r, T, float(Strike), 3, 'P')
        
        theo_c_BS = price_option(price, float(Strike), r, q, s_vol, T, 0)
        theo_p_BS = price_option(price, float(Strike), r, q, s_vol, T, 1)
        
        if theo_c_BI[0] >= 0 and theo_p_BI[0] >= 0 and theo_c_BS >= 0 and theo_p_BS >= 0:
     
            summary_data.update({'Open(C)':O_C})
            summary_data.update({'Settle(C)':S_C})
            summary_data.update({'Change(C)':S_C_C})
            if S_C_C == '-':
                summary_data.update({'Change(C%)':'-'})
            else:
                summary_data.update({'Change(C%)':round(100*float(S_C_C)/(float(S_C)-float(S_C_C)),2)})
            
            summary_data.update({'T-Price(tree,C)':round(theo_c_BI[0],2)})
            summary_data.update({'T-Price(BS,C)':round(theo_c_BS,2)})
    
            summary_data.update({'Open(P)':O_P})
            summary_data.update({'Settle(P)':S_P})
            summary_data.update({'Change(P)':S_P_C})
            if S_P_C == '-':
                summary_data.update({'Change(P%)':'-'})
            else:
                summary_data.update({'Change(P%)':round(100*float(S_P_C)/(float(S_P)-float(S_P_C)),2)})
                
            summary_data.update({'T-Price(tree,P)':round(theo_p_BI[0],2)})
            summary_data.update({'T-Price(BS,P)':round(theo_p_BS,2)})
        
        else:
            summary_data.clear()
    
    else:
        summary_data.clear()
     
    return summary_data                           


def get_delta(S, K, r, q, sigma, T, t_o):

    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        if t_o == 0:
            delta = math.exp(-1*q*T)*norm.cdf(d1)
        else:
            delta = math.exp(-1*q*T)*(norm.cdf(d1)-1)
    else:
        delta = -1

    return delta


def get_vega(S, K, r, q, sigma, T):

    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        vega = (1/100)*S*math.exp(-1*q*T)*math.sqrt(T)*(1/math.sqrt(2*math.pi))*math.exp(-1*d1*d1/2)
    else:
        vega = -1

    return vega


def binomialTree(S0, volatility, rate, time, strike, steps, CorP):
    
    smallT = float(time)/steps

    if volatility != 0 and smallT > 0:
        up = math.exp(volatility * math.sqrt(smallT))
        down = 1.0 / up
        
        prob = (math.exp(rate * smallT) - down)/(up - down)
        
        df = math.exp(-1 * rate * smallT)
        
        call = False
        if CorP == "C":
            call = True
        
        binomialSet = []
        oriPrice = [S0]
        binomialSet.append(oriPrice)
    
        #initial each step price
        for i in range(1, steps+1):
            pricelist = []
            prePriceList = binomialSet[i - 1]
            for j in range(0, i+1):
                if j < i:
                    price = prePriceList[j] * up
                else:
                    price = prePriceList[j-1] * down
                pricelist.append(price)
            binomialSet.append(pricelist)
    
        i = steps
        optionPriceSet = []
        
        #calculate call option price
        if call:
            finaloptionPrilist = []
            for price in binomialSet[steps]:
    
                if price > strike:
                    finaloptionPrilist.append(price-strike)
                else:
                    finaloptionPrilist.append(0)
            optionPriceSet.append(finaloptionPrilist)
    
            while i >= 1:
                pricelist = binomialSet[i-1]
                optionPrice = []
                preOptionPrice = optionPriceSet[steps-i]
                for j in range(0, len(pricelist)):
                    tmp = pricelist[j] - strike
                    dfprice = df * ((1-prob) * preOptionPrice[j+1] +  prob * preOptionPrice[j])
                    optionPrice.append(max(tmp, dfprice, 0))
                optionPriceSet.append(optionPrice)
                i = i-1
    
        # calculate put option price
        if not call:
            finaloptionPrilist = []
            for price in binomialSet[steps]:
    
                if price < strike:
                    finaloptionPrilist.append(strike - price)
                else:
                    finaloptionPrilist.append(0)
            optionPriceSet.append(finaloptionPrilist)
    
            while i >= 1:
                pricelist = binomialSet[i - 1]
                optionPrice = []
                preOptionPrice = optionPriceSet[steps - i]
                for j in range(0, len(pricelist)):
                    tmp = strike - pricelist[j]
                    dfprice = df * ((1- prob)* preOptionPrice[j + 1] +  prob * preOptionPrice[j])
                    optionPrice.append(max(tmp, dfprice, 0))
                optionPriceSet.append(optionPrice)
                i = i - 1
    else:
        a = [-1]
        return a
        
        
    return optionPriceSet[-1]


def price_option(S, K, r, q, sigma, T, t_o):
    
    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        
        if t_o == 0:
            C = S*math.exp(-1*q*(T))*norm.cdf(d1) - K*math.exp(-1*r*(T))*norm.cdf(d2)
            return C
        else:
            P = K*math.exp(-1*r*(T))*norm.cdf(-1*d2) - S*math.exp(-1*q*(T))*norm.cdf(-1*d1)
            return P
    else:
        return -1


def get_s_vol(underlying, lastdate, m = 21):

    stock_code = 'HKEX/' + underlying

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = m * 3))

    try:
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)
    except:
        sleep(10)
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)

    data = np.array(list(price_BB[-(m+1):]['Nominal Price']))

    X = []
    Xsum = 0
    if len(data)>2:
        for i in range(len(data)-1):
            X.append(math.log(data[len(data)-i-1]/data[len(data)-i-2]))
            
        mu = np.array(X).mean()
        #deltaT = 1/252
        Xsum = sum([ (x-mu)*(x-mu) for x in X])
        s_vol = math.sqrt(252 * Xsum / (m - 1))

    else:
        s_vol = 0.00

    return s_vol
    

def get_BBands(code, lastdate, period = 26):

    stock_code = 'HKEX/' + code

    mu = 0
    sigma = 0
    net_change = 0
    change_per = 0

    last_date = datetime.strptime(lastdate,'%Y-%m-%d')
    
    right = str(last_date)
    left = str(last_date - timedelta(days = period * 3))

    try:
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)
    except:
        sleep(15)
        price_BB = quandl.get(stock_code, start_date = left , end_date = right)

    if len(price_BB)==1:

        u_d = '-'
  
        quote = price_BB[-1:]['Nominal Price']
        net_change = '-'
        change_per = '-'

    elif len(price_BB)==0: #has option, but stock is still not on list

        u_d = '-'
        quote = 0.00
        net_change = '-'
        change_per = '-'

    else:
        data = np.array(list(price_BB[-period:]['Nominal Price']))
        mu = np.mean(data)

        quote = price_BB[-1:]['Nominal Price']
        quote_yes = price_BB[-2:-1]['Nominal Price']
        net_change = round(float(quote)-float(quote_yes),2)
        change_per = round(100*(float(quote)-float(quote_yes))/float(quote_yes),2)
        
        sigma = np.std(data)
        upper = mu + 2*sigma
        down = mu - 2*sigma  

        if float(quote) >= upper:
            u_d = 'up'
        elif float(quote) <= down:
            u_d = 'down'
        else:
            u_d = '-'

    return u_d,net_change,change_per,float(quote)


#def get_index():
#
#    url = "https://www.bloomberg.com/quote/HSI:IND/members"
#    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
#    acceptEncoding = 'gzip, deflate, br'
#    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
#    response = requests.get(url,headers={"User-Agent":user_agent, "Accept":accept, "accept-encoding":acceptEncoding})
#    s=response.text
#    parser = html.fromstring(s)
#
#    index = parser.xpath('//div[@class="index-members"]/div[1]/div[@class="index-members"]/div[@class="security-summary"]')
#
#    s_index = []
#    
#    for mem in index:
#        ticker = mem.xpath('.//a[contains(@class,"ticker")]//text()')
#        temp = str(ticker[0])[:-3]
#        s_index.append(temp)
#  
#    return s_index


if __name__=="__main__":

    code, underlying = get_code()

#    expiry_list = ['JAN18','FEB18','MAR18','APR18','MAY18','JUN18','JUL18','AUG18','SEP18','OCT18','NOV18','DEC18']
    expiry_list = ['JAN18','FEB17','MAR17','APR17','MAY17','JUN17','JUL17','AUG17','SEP17','OCT17','NOV17','DEC17']
#    maturity_list = [30,27,28,27,30,28,30,30,27,30,29, 28]
    maturity_list = [30,27,28,27,30,28, 28,30,28,30,29,28]
    
    special_list = ['2017-07-31','2017-08-31','2017-09-29','2017-10-31','2017-11-30','2017-12-29', \
                    '2018-01-31','2018-02-28','2018-03-29','2018-04-30','2018-05-31','2018-06-29', \
                    '2018-07-31','2018-08-31','2018-09-28','2018-10-31','2018-11-30']
    
#    time_list_1 = ['2018-01-02','2018-01-03','2018-01-04','2018-01-05', \
#                   '2018-01-08','2018-01-09','2018-01-10','2018-01-11','2018-01-12', \
#                   '2018-01-15','2018-01-16','2018-01-17','2018-01-18','2018-01-19', \
#                   '2018-01-22','2018-01-23','2018-01-24','2018-01-25','2018-01-26', \
#                   '2018-01-29']

#    time_list_2 = ['2018-02-01','2018-02-02', \
#                   '2018-02-05','2018-02-06','2018-02-07','2018-02-08','2018-02-09', \
#                   '2018-02-12','2018-02-13','2018-02-14','2018-02-15', \
#                   '2018-02-20','2018-02-21','2018-02-22','2018-02-23', \
#                   '2018-02-26']

#    time_list_3 = ['2018-03-01','2018-03-02', \
#                   '2018-03-05','2018-03-06','2018-03-07','2018-03-08','2018-03-09', \
#                   '2018-03-12','2018-03-13','2018-03-14','2018-03-15','2018-03-16', \
#                   '2018-03-19','2018-03-20','2018-03-21','2018-03-22','2018-03-23', \
#                   '2018-03-26','2018-03-27']

#    time_list_4 = ['2018-04-03','2018-04-04','2018-04-06', \
#                   '2018-04-09','2018-04-10','2018-04-11','2018-04-12','2018-04-13', \
#                   '2018-04-16','2018-04-17','2018-04-18','2018-04-19','2018-04-20', \
#                   '2018-04-23','2018-04-24','2018-04-25','2018-04-26']

#    time_list_5 = ['2018-05-02','2018-05-03','2018-05-04', \
#                   '2018-05-07','2018-05-08','2018-05-09','2018-05-10',2018-05-11', \
#                   '2018-05-14','2018-05-15','2018-05-16','2018-05-17','2018-05-18', \
#                   '2018-05-21','2018-05-23','2018-05-24','2018-05-25', \
#                   '2018-05-28','2018-05-29']
    
#    time_list_6 = ['2018-06-01', \
#                   '2018-06-04','2018-06-05','2018-06-06','2018-06-07','2018-06-08', \
#                   '2018-06-11','2018-06-12','2018-06-13','2018-06-14','2018-06-15', \
#                   '2018-06-19','2018-06-20','2018-06-21','2018-06-22', \
#                   '2018-06-25','2018-06-26','2018-06-27']

#    time_list_7 = ['2018-07-03','2018-07-04','2018-07-05','2018-07-06',\
#                   '2018-07-09','2018-07-10','2018-07-11','2018-07-12','2018-07-13', \
#                   '2018-07-16','2018-07-17','2018-07-18','2018-07-19','2018-07-20', \
#                   '2018-07-23','2018-07-24','2018-07-25','2018-07-26','2018-07-27', \
#                   ]
    
#    time_list_7 = ['2017-07-03','2017-07-04','2017-07-05','2017-07-06','2017-07-07', \
#                   '2017-07-10','2017-07-11','2017-07-12','2017-07-13','2017-07-14', \
#                   '2017-07-17','2017-07-18','2017-07-19','2017-07-20','2017-07-21', \
#                   '2017-07-24','2017-07-25','2017-07-26','2017-07-27', \
#                   ]
    
#    time_list_8 = ['2018-08-01','2018-08-02','2018-08-03',\
#                   '2018-08-06','2018-08-07','2018-08-08','2018-08-09','2018-08-10', \
#                   '2018-08-13','2018-08-14','2018-08-15','2018-08-16','2018-08-17', \
#                   '2018-08-20','2018-08-21','2018-08-22','2018-08-23','2018-08-24', \
#                   '2018-08-27','2018-08-28','2018-08-29']

#    time_list_8 = ['2017-08-01','2017-08-02','2017-08-03','2017-08-04',\
#                   '2017-08-07','2017-08-08','2017-08-09','2017-08-10','2017-08-11',\
#                   '2017-08-14','2017-08-15','2017-08-16','2017-08-17','2017-08-18', \
#                   '2017-08-21','2017-08-22','2017-08-23','2017-08-24','2017-08-25', \
#                   '2017-08-28','2017-08-29']

#    time_list_9 = ['2018-09-03','2018-09-04','2018-09-05','2018-09-06','2018-09-07', \
#                   '2018-09-10','2018-09-11','2018-09-12','2018-09-13','2018-09-14', \
#                   '2018-09-17','2018-09-18','2018-09-19',
#                   '2018-09-20','2018-09-21', \
#                   '2018-09-24','2018-09-26']
    
#    time_list_9 = ['2017-09-01', \
#                   '2017-09-04','2017-09-05','2017-09-06','2017-09-07','2017-09-08', \
#                   '2017-09-11','2017-09-12','2017-09-13','2017-09-14','2017-09-15', \
#                   '2017-09-18','2017-09-19','2017-09-20','2017-09-21','2017-09-22', \
#                   '2017-09-25',]
    
#    time_list_10 = ['2018-10-02','2018-10-03','2018-10-04','2018-10-05', \
#                   '2018-10-08','2018-10-09','2018-10-10','2018-10-11','2018-10-12', \
#                   '2018-10-15','2018-10-16','2018-10-18','2018-10-19', \
#                   '2018-10-22','2018-10-23','2018-10-24','2018-10-25','2018-10-26', \
#                   '2018-10-29']
    
#    time_list_10 = ['2017-10-03','2017-10-04','2017-10-06', \
#                   '2017-10-09','2017-10-10','2017-10-11','2017-10-12','2017-10-13', \
#                   '2017-10-16','2017-10-17','2017-10-18','2017-10-19','2017-10-20', \
#                   '2017-10-23','2017-10-24','2017-10-25','2017-10-26','2017-10-27', \
#                   ]

#    time_list_11 = ['2018-11-01','2018-11-02', \
#                   '2018-11-05','2018-11-06','2018-11-07','2018-11-08','2018-11-09', \
#                   '2018-11-12','2018-11-13','2018-11-14','2018-11-15','2018-11-16', \
#                   '2018-11-19','2018-11-20','2018-11-21','2018-11-22','2018-11-23', \
#                   '2018-11-26','2018-11-27','2018-11-28']
    
#    time_list_11 = ['2017-11-01','2017-11-02','2017-11-03', \
#                   '2017-11-06','2017-11-07','2017-11-08','2017-11-09','2017-11-10', \
#                   '2017-11-13','2017-11-14','2017-11-15','2017-11-16','2017-11-17', \
#                   '2017-11-20','2017-11-21','2017-11-22','2017-11-23','2017-11-24', \
#                   '2017-11-27','2017-11-28']
    
#    time_list_12 = ['2017-12-01', \
#                   '2017-12-04','2017-12-05','2017-12-06','2017-12-07','2017-12-08', \
#                   '2017-12-11','2017-12-12','2017-12-13','2017-12-14','2017-12-15', \
#                   '2017-12-18','2017-12-19','2017-12-20','2017-12-21','2017-12-22', \
#                   '2017-12-27']  

    time_list_special = ['2017-11-30']
    
    for u_time in time_list_special:
        
        m = int(u_time[5:7].lstrip('0'))
        
        if u_time in special_list:
            expiry = expiry_list[m % 12]
        else:
            expiry = expiry_list[(m-1) % 12]
        
        HSI_close = pd.read_excel("HSI.xlsx")
        index = HSI_close[(HSI_close['Date'] == u_time)].index.tolist()[0]
        HSI_price = HSI_close.iloc[index,1]
        
        url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(u_time.replace("-", "")[2:])

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        response = webdriver.Chrome(options=chrome_options)

        response.get(url)
        sleep(3)

        data = pd.DataFrame()
        cols=[]

        for i in range(len(code)):
            try:
                o_data = response.find_element_by_name(code[i])
            except:
                continue

            o_data = o_data.text.split('\n')
            summary_data = get_option(code[i], underlying[i], o_data, u_time, expiry, maturity_list[m-1], float(HSI_price))
            if summary_data:
                print(summary_data)
                cols = summary_data.keys()
                price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
                data = pd.concat([data, price_data], sort=True)
                  
        if not os.path.exists('option_data/'):
            os.makedirs('option_data/')

        file_name = 'option_data' + '/option_' + u_time
        data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


