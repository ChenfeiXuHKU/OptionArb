from __future__ import division
from collections import OrderedDict
import os
import pandas as pd
from lxml import html  
import requests 

#%%
name = './hsio_data/hsio.csv'
data = pd.read_csv(name)

arb_data = pd.DataFrame()
cols=[]
               
    
for i in range(len(data)-1):
    date = data.loc[i+1,'Date']
    strike = data.loc[i, 'HSI Strike']
    
    summary_data = OrderedDict()
                
    url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio{0}.htm".format(date.replace("-", "")[2:])
    
    response = requests.get(url)
    s=response.text
    parser = html.fromstring(s)
    
    hsi_data = parser.xpath('/html/body/pre/text()')
    hsi_o = hsi_data[1].split('\n')
    #print(hsi_o)        
    summary_data.update({'Date':date})
    summary_data.update({'Strike':float(strike)})
    
    index_hsi_c = 0
    index_hsi_p = 0
    
    if len(hsi_o) > 0:
        for i in range(len(hsi_o)):
            w = hsi_o[i].split()
            if len(w) > 2 and w[2] == 'C':
                c = w[1]
                if float(c) == float(strike):
                    index_hsi_c = i
            elif len(w) > 2 and w[2] == 'P':
                p = w[1]
                if float(p) == float(strike):
                    index_hsi_p = i
                    break
            
    if index_hsi_c != 0 and index_hsi_p != 0:
        if len(hsi_o[index_hsi_c].split()) > 12:   
            
            summary_data.update({'Open(C)':float(hsi_o[index_hsi_c].split()[9])})
            summary_data.update({'Settle(C)':float(hsi_o[index_hsi_c].split()[12])})
            summary_data.update({'Change(C)':float(hsi_o[index_hsi_c].split()[13])})

            summary_data.update({'Open(P)':float(hsi_o[index_hsi_p].split()[9])})
            summary_data.update({'Settle(P)':float(hsi_o[index_hsi_p].split()[12])})
            summary_data.update({'Change(P)':float(hsi_o[index_hsi_p].split()[13])})

        else:
            
            summary_data.update({'Open(C)':float(hsi_o[index_hsi_c].split()[3])})
            summary_data.update({'Settle(C)':float(hsi_o[index_hsi_c].split()[6])})
            summary_data.update({'Change(C)':float(hsi_o[index_hsi_c].split()[7])})
                
            summary_data.update({'Open(P)':float(hsi_o[index_hsi_p].split()[3])})
            summary_data.update({'Settle(P)':float(hsi_o[index_hsi_p].split()[6])})
            summary_data.update({'Change(P)':float(hsi_o[index_hsi_p].split()[7])})
                        
                        
    if summary_data:
        print(summary_data)
        cols = summary_data.keys()
        price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
        arb_data = pd.concat([arb_data, price_data], sort=True)
                    
file_name = 'hsio_data/' + 'hsio_arb'
arb_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)


                  
        









