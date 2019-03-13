from __future__ import division
import pandas as pd
from datetime import datetime 
from collections import OrderedDict
from datetime import timedelta
import os

#%%
def get_data(begin, end, dim):
        
    month_data =  pd.DataFrame()
    
    while begin != end:       
        C_data = OrderedDict()
        P_data = OrderedDict()         
        C_data_pd = pd.DataFrame()
        P_data_pd = pd.DataFrame()      
        one_data = pd.DataFrame()      
        data = pd.read_csv('../option_data/option_' + begin + '.csv')
        
        #for call options one day
        for i in range(len(data)):
            code = data.loc[i,'Option Code']
            if data.loc[i,'Change(C%)'] == '-':
                continue
            else:
                C_change = float(data.loc[i,'Change(C%)'])            
            if data.loc[i,'Change(HSIo,C%)'] == '-':
                continue
            else:  
                C_benchmark = float(data.loc[i,'Change(HSIo,C%)'])
                
            if C_change >= C_benchmark:
                C_data.update({code:[1]})
            else:
                C_data.update({code:[0]})    
                
            days = 0
            temp_date = begin
            while(days < dim):
                #search previous trading day
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
                while((not os.path.exists('../option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                u_time = last_date[0:10]
                last_data = pd.read_csv('../option_data/option_' + u_time + '.csv')
                
                #get max change value at that day
                changes_c = last_data['Change(C%)'].tolist()
                while '-' in changes_c:
                    changes_c.remove('-')
                temp_changes_c_max = max([float(cc) for cc in changes_c])
                temp_changes_c_min = min([float(cc) for cc in changes_c])        
                #get change value for one option at that day
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                if last_data.loc[last_index,'Change(C%)'] == '-':
                    break
                else:
                    temp_C_change = float(last_data.loc[last_index,'Change(C%)'])     
                #normalize change value and store
                if temp_changes_c_max == 0:
                    c_scale = abs(temp_changes_c_min)
                    C_data[code].append(temp_C_change / c_scale)        
                elif temp_changes_c_min == 0:
                    c_scale = abs(temp_changes_c_max)
                    C_data[code].append(temp_C_change / c_scale)
                else:
                    if abs(temp_changes_c_max) >= abs(temp_changes_c_min):
                        c_scale = abs(temp_changes_c_max)
                    else:
                        c_scale = abs(temp_changes_c_min)
            
                    C_data[code].append(temp_C_change / c_scale)

                #get max volume at that day
                volumes_c = last_data['Volume(C)'].tolist()
                while '-' in volumes_c:
                    volumes_c.remove('-')
                temp_c_vol_max = max([int(str(vc).replace(',','')) for vc in volumes_c])            
                #get volume for above option at that day
                if last_data.loc[last_index,'Volume(C)'] == '-':
                    break
                else:
                    temp_C_volume = int(str(last_data.loc[last_index,'Volume(C)']).replace(',',''))
                #normalize volume
                if temp_c_vol_max == 0:
                    C_data[code].append(0)        
                else:
                    C_data[code].append(temp_C_volume / abs(temp_c_vol_max))

                days = days + 1
                temp_date = u_time          
            
            #add label
            if len(C_data[code]) != (dim*2 + 1):
                del C_data[code]
                
                
        #for put options one day
        for i in range(len(data)):
            code = data.loc[i,'Option Code']
            if data.loc[i,'Change(P%)'] == '-':
                continue
            else:
                P_change = float(data.loc[i,'Change(P%)'])   
            if data.loc[i,'Change(HSIo,P%)'] == '-':
                continue
            else:  
                P_benchmark = float(data.loc[i,'Change(HSIo,P%)'])
            
            if P_change >= P_benchmark:
                P_data.update({code:[1]})
            else:
                P_data.update({code:[0]})
                    
            days = 0
            temp_date = begin
            while(days < dim):
                #search previous trading day
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
                while((not os.path.exists('../option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                u_time = last_date[0:10]
                last_data = pd.read_csv('../option_data/option_' + u_time + '.csv')
                
                #get max change value at that day
                changes_p = last_data['Change(P%)'].tolist()
                while '-' in changes_p:
                    changes_p.remove('-')
                temp_changes_p_max = max([float(cp) for cp in changes_p])
                temp_changes_p_min = min([float(cp) for cp in changes_p])
                #get change value for one option at that day
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                if last_data.loc[last_index,'Change(P%)'] == '-':
                    break
                else:
                    temp_P_change = float(last_data.loc[last_index,'Change(P%)'])       
                #normalize change value and store
                if temp_changes_p_max == 0:
                    p_scale = abs(temp_changes_p_min)
                    P_data[code].append(temp_P_change / p_scale)       
                elif temp_changes_p_min == 0:
                    p_scale = abs(temp_changes_p_max)
                    P_data[code].append(temp_P_change / p_scale) 
                else:
                    if abs(temp_changes_p_max) >= abs(temp_changes_p_min):
                        p_scale = abs(temp_changes_p_max)
                    else:
                        p_scale = abs(temp_changes_p_min)
                    P_data[code].append(temp_P_change / p_scale) 

                #get max volume at that day
                volumes_p = last_data['Volume(P)'].tolist()
                while '-' in volumes_p:
                    volumes_p.remove('-')
                temp_p_vol_max = max([int(str(vp).replace(',','')) for vp in volumes_p])          
                #get volume for above option at that day
                if last_data.loc[last_index,'Volume(P)'] == '-':
                    break
                else:
                    temp_P_volume = int(str(last_data.loc[last_index,'Volume(P)']).replace(',','')) 
                #normalize volume
                if temp_p_vol_max == 0:
                    P_data[code].append(0)        
                else:
                    P_data[code].append(temp_P_volume / abs(temp_p_vol_max))

                days = days + 1
                temp_date = u_time          
            
            #add label
            if len(P_data[code]) != (dim*2 + 1):
                del P_data[code]
        
        #merge both options at one day
        if C_data or P_data:
            C_data_pd = pd.DataFrame.from_dict(C_data, orient='index').T
            P_data_pd = pd.DataFrame.from_dict(P_data, orient='index').T
            one_data = pd.concat([C_data_pd, P_data_pd], axis = 1)
            month_data = pd.concat([month_data, one_data], axis = 1)
        
        #search next trading day
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        while((not os.path.exists('../option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10] < '2018-12-28'):
            count = count + 1
            next_date = str(begin_date + timedelta(days = count))
        begin = next_date[0:10]
        
    return month_data

#%%
if __name__=="__main__":  

    # for 5 features
    begin_ends_5 = [
#            ['2017-07-10','2017-07-31'],
#            ['2017-08-07','2017-08-31'],
#            ['2017-09-07','2017-10-03'],
#            ['2017-10-11','2017-10-31'],
#            ['2017-11-07','2017-11-30'],
            ['2017-12-07','2017-12-29'],
            ['2018-01-08','2018-01-31'],
            ['2018-02-07','2018-02-28'],
            ['2018-03-07','2018-03-29'],
            ['2018-04-10','2018-04-30'],
            ['2018-05-08','2018-05-31'],
            ['2018-06-07','2018-06-29'],
            ['2018-07-09','2018-07-31'],
            ['2018-08-07','2018-08-31'],
            ['2018-09-07','2018-09-28'],
            ['2018-10-08','2018-10-31'],
            ['2018-11-07','2018-11-30'],
            ]
    
    # for 10 features
    begin_ends_10 = [
            ['2017-07-17','2017-07-31'],
            ['2017-08-14','2017-08-31'],
            ['2017-09-14','2017-10-03'],
            ['2017-10-18','2017-10-31'],
            ['2017-11-14','2017-11-30'],
            ['2017-12-14','2017-12-29'],
            ['2018-01-15','2018-01-31'],
            ['2018-02-14','2018-02-28'],
            ['2018-03-14','2018-03-29'],
            ['2018-04-17','2018-04-30'],
            ['2018-05-15','2018-05-31'],
            ['2018-06-14','2018-06-29'],
            ['2018-07-16','2018-07-31'],
            ['2018-08-14','2018-08-31'],
            ['2018-09-14','2018-09-28'],
            ['2018-10-15','2018-10-31'],
            ['2018-11-14','2018-11-30'],
            ] 
    
    for i in range(len(begin_ends_5)):
        month_data = get_data(begin_ends_5[i][0], begin_ends_5[i][1], 5)
        
        file_name = '../train_data/' + 'train_data_5d_' + begin_ends_5[i][0][0:7]
        month_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
    
    
    
    
    
    
    
    