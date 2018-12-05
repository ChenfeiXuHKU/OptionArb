from __future__ import division
import pandas as pd
import numpy as np
from datetime import datetime 
from time import sleep
from collections import OrderedDict
from datetime import timedelta
import os


#%%
def get_data(begin, end, dim):
        
    # one day for one 'epoch', mini-dataset is about dim x 90 
    C_data = OrderedDict()
    P_data = OrderedDict()
        
    C_data_pd = pd.DataFrame()
    P_data_pd = pd.DataFrame()
    
    month_data =  pd.DataFrame()
    
    while begin != end:
        
        data = pd.read_csv('option_data/option_' + begin + '.csv')
        
        for i in range(len(data)):
            code = data.loc[i,'Option Code']
            C_change = data.loc[i,'Change(C%)']
            P_change = data.loc[i,'Change(P%)']
            C_benchmark = data.loc[i,'Change(HSIo,C%)']
            P_benchmark = data.loc[i,'Change(HSIo,P%)']

#            
            C_data.update({code:[C_change]})
            P_data.update({code:[P_change]})
                
            days = 0
            
            temp_date = begin
            while(days < (dim - 1)):
            
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
        
                while((not os.path.exists('option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10]>='2018-05-02'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                
                u_time = last_date[0:10]
            
                last_data = pd.read_csv('option_data/option_' + u_time + '.csv')
                
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                
                C_data[code].append(last_data.loc[last_index,'Change(C%)'])
                P_data[code].append(last_data.loc[last_index,'Change(P%)'])
    
                days = days + 1
            
                temp_date = u_time    
                
            
            if len(C_data[code]) == dim:
                print(C_data)
                    
                 if C_change >= C_benchmark:
                    C_data[code].append(1)
                else:
                    C_data[code].append(0)
            
            else:
                del C_data[code]
            
            if len(P_data[code]) == dim:
                print(P_data)
                    
                if P_change >= P_benchmark:
                    P_data[code].append(1)
                else:
                    P_data[code].append(0)
            
            else:
                del P_data[code]
                
                
        #cols = summary_data.keys()
        C_data_pd = pd.DataFrame.from_dict(C_data, orient='index').T
        P_data_pd = pd.DataFrame.from_dict(P_data, orient='index').T
        one_data = pd.concat([C_data_pd, P_data_pd], axis = 1)
        month_data = pd.concat([month_data, one_data], axis = 1)
        
                    
        file_name = 'train_data' + '/train_data_May_' + str(dim)
        month_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
            
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        
        while((not os.path.exists('option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10]<='2018-10-01'):
                count = count + 1
                next_date = str(begin_date + timedelta(days = count))
        begin = next_date[0:10]
        
    
    return 0


if __name__=="__main__":  


    begin = '2018-05-08'
    end = '2018-05-29'
    
    get_data(begin,end,5)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    