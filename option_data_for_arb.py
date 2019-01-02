from __future__ import division
import pandas as pd
from datetime import datetime 
from time import sleep
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import os

#%%
def get_arb_data(begin, end):
	
    while begin != end:
        summary_data = OrderedDict()
        arb_data = pd.DataFrame()
        cols=[]
        data = pd.read_csv('option_data/option_' + begin + '.csv')
            
        current_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(current_date + timedelta(days = count))
        while((not os.path.exists('option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-12-31'):
            count = count + 1
            next_date = str(current_date + timedelta(days = count))
        u_time = next_date[0:10]
            
        url = "http://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{0}.htm".format(u_time.replace("-", "")[2:])
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        response = webdriver.Chrome(options=chrome_options)
        response.get(url)
        sleep(3)
                
        for i in range(len(data)):
            summary_data.update({'Date':u_time})
            code = data.loc[i,'Option Code']
            strike = data.loc[i, 'Strike']
            try:
                o_data = response.find_element_by_name(code)
            except:
                print("code not existed")
                continue
        
            summary_data.update({'Option Code':code})
            summary_data.update({'Strike':float(strike)})
            o_data = o_data.text.split('\n')
            expiry = o_data[10].split()[0]
                
            for i in range(len(o_data)):
                w = o_data[i].split()
                if len(w) == 12 and w[2] == 'C' and float(w[1]) == float(strike) and w[0] == expiry:
                    summary_data.update({'Open(C)':float(w[3])})
                    summary_data.update({'Settle(C)':float(w[6])})
                    summary_data.update({'IV(C)':w[8]})
                    
                if len(w) == 12 and w[2] == 'P' and float(w[1]) == float(strike) and w[0] == expiry:
                    summary_data.update({'Open(P)':float(w[3])})
                    summary_data.update({'Settle(P)':float(w[6])})
                    summary_data.update({'IV(P)':w[8]})
                    break
            
            if summary_data:
                print(summary_data)
                cols = summary_data.keys()
                price_data = pd.DataFrame.from_dict(summary_data, orient='index').T       
                arb_data = pd.concat([arb_data, price_data], sort=True)
                    
        file_name = 'option_data' + '/arb_data_' + u_time
        arb_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', columns=cols, index=False)
  
        begin = u_time
        
    return 0

begin_ends = [
#            ['2018-01-31','2018-02-26'],
#            ['2018-02-28','2018-03-27'],
#            ['2018-03-29','2018-04-26'],
#            ['2018-04-30','2018-05-29'],
#            ['2018-05-31','2018-06-27'],
#            ['2018-06-29','2018-07-27'],
#            ['2018-07-31','2018-08-29'],
#            ['2018-08-31','2018-09-26'],
#            ['2018-09-28','2018-10-29'],
#            ['2018-10-31','2018-11-28'],
            ['2018-11-30','2018-12-27'],
            ] 
    
for i in range(len(begin_ends)):
    get_arb_data(begin_ends[i][0],begin_ends[i][1])
                  
        









