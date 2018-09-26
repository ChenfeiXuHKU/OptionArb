from __future__ import division
from collections import OrderedDict
import os
import pandas as pd
from lxml import html  
import requests  

def get_HSI_option(u_time, hsi_price):

    summary_data = OrderedDict()

    summary_data.update({'Date':u_time})
    
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
    
    else:
        summary_data.clear()
     
    return summary_data                           


if __name__=="__main__":

    
    special_list = ['2018-04-30', '2018-05-31', '2018-06-29', '2018-07-31']
    
    #time_list_4 = ['2018-04-03','2018-04-04','2018-04-06','2018-04-09','2018-04-10','2018-04-11','2018-04-12','2018-04-13', '2018-04-16', '2018-04-17', '2018-04-18', '2018-04-19', '2018-04-20','2018-04-23','2018-04-24','2018-04-25','2018-04-26','2018-04-27']
    time_list_5 = ['2018-05-02','2018-05-03','2018-05-04','2018-05-07','2018-05-08','2018-05-09','2018-05-10','2018-05-11',\
                   '2018-05-14', '2018-05-15', '2018-05-16', '2018-05-17', '2018-05-18',\
                   '2018-05-21','2018-05-23','2018-05-24','2018-05-25',\
                   '2018-05-28', '2018-05-29', '2018-05-30','2018-05-31',\
                   '2018-06-01','2018-06-04','2018-06-05','2018-06-06','2018-06-07','2018-06-08',\
                   '2018-06-11','2018-06-12','2018-06-13','2018-06-14','2018-06-15',\
                   '2018-06-19','2018-06-20','2018-06-21','2018-06-22',\
                   '2018-06-25','2018-06-26','2018-06-27','2018-06-28','2018-06-29',\
                   '2018-07-03','2018-07-04','2018-07-05','2018-07-06',\
                   '2018-07-09','2018-07-10','2018-07-11','2018-07-12','2018-07-13',\
                   '2018-07-16','2018-07-17','2018-07-18','2018-07-19','2018-07-20',\
                   '2018-07-23','2018-07-24','2018-07-25','2018-07-26','2018-07-27',\
                   '2018-07-30','2018-07-31']

    data = pd.DataFrame()
    cols=[]
        
    for u_time in time_list_5:
        
        HSI_close = pd.read_excel("HSI.xlsx")
        index = HSI_close[(HSI_close['Date'] == u_time)].index.tolist()[0]
        HSI_price = HSI_close.iloc[index,1]
       
        summary_data = get_HSI_option(u_time, float(HSI_price))
        if summary_data:
            print(summary_data)
            cols = summary_data.keys()
            price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
            data = pd.concat([data, price_data], sort=True)
                  
    if not os.path.exists('hsio_data/'):
        os.makedirs('hsio_data/')
        
    file_name = 'hsio_data' + '/hsio'
    data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


