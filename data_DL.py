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
        
        data = pd.read_csv('option_data/option_' + begin + '.csv')
        
        volumes_c = data['Volume(C)'].tolist()
        c_vol_max = max([int(str(vc).replace(',','')) for vc in volumes_c])
         
        changes_c = data['Change(C%)'].tolist()
        while '-' in changes_c:
            changes_c.remove('-')
            
        changes_c_max = max([float(cc) for cc in changes_c])
        changes_c_min = min([float(cc) for cc in changes_c])
        
        volumes_p = data['Volume(P)'].tolist()
        p_vol_max = max([int(str(vp).replace(',','')) for vp in volumes_p])
        
        changes_p = data['Change(P%)'].tolist()
        while '-' in changes_p:
            changes_p.remove('-')
            
        changes_p_max = max([float(cp) for cp in changes_p])
        changes_p_min = min([float(cp) for cp in changes_p])
        #print(data['Change(C%)'])
        
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
            
            C_volume = float(str(data.loc[i,'Volume(C)']).replace(',','')) / c_vol_max

            if C_change >= 0:
                c_scale = abs(changes_c_max)
            else:
                c_scale = abs(changes_c_min)
            
            if changes_c_max == 0:
                c_scale = abs(changes_c_min)
                C_data.update({code:[C_volume, C_change / c_scale]})
                
            elif changes_c_min == 0:
                c_scale = abs(changes_c_max)
                C_data.update({code:[C_volume, C_change / c_scale]})
                
            else:
                C_data.update({code:[C_volume, C_change / c_scale]})
      
            days = 0
            
            temp_date = begin
            while(days < (dim - 1)):
            
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
        
                while((not os.path.exists('option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                
                u_time = last_date[0:10]
                last_data = pd.read_csv('option_data/option_' + u_time + '.csv')
                
                changes_c = last_data['Change(C%)'].tolist()
                while '-' in changes_c:
                    changes_c.remove('-')
                
                temp_changes_c_max = max([float(cc) for cc in changes_c])
                temp_changes_c_min = min([float(cc) for cc in changes_c])

                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                
                if last_data.loc[last_index,'Change(C%)'] == '-':
                    days = days + 1
                    continue
                else:
                    temp_C_change = float(last_data.loc[last_index,'Change(C%)'])
            
                if temp_C_change >= 0:
                    c_scale = abs(temp_changes_c_max)
                else:
                    c_scale = abs(temp_changes_c_min)                
                
                if temp_changes_c_max == 0:
                    c_scale = abs(temp_changes_c_min)
                    C_data[code].append(temp_C_change / c_scale)
            
                elif temp_changes_c_min == 0:
                    c_scale = abs(temp_changes_c_max)
                    C_data[code].append(temp_C_change / c_scale)
                    
                else:
                    C_data[code].append(temp_C_change / c_scale)

                days = days + 1
                temp_date = u_time          
            
            if len(C_data[code]) == (dim + 1):
                    
                if C_change >= C_benchmark:
                    C_data[code].append(1)
                else:
                    C_data[code].append(0)
            
            else:
                del C_data[code]

       
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
            
            P_volume = float(str(data.loc[i,'Volume(P)']).replace(',','')) / p_vol_max
            
            if P_change >= 0:
                p_scale = abs(changes_p_max)
            else:
                p_scale = abs(changes_p_min)
            
            if changes_p_max == 0:
                p_scale = abs(changes_p_min)
                P_data.update({code:[P_volume, P_change / p_scale]})
                
            elif changes_p_min == 0:
                p_scale = abs(changes_p_max)
                P_data.update({code:[P_volume, P_change / p_scale]})
                
            else:
                P_data.update({code:[P_volume, P_change / p_scale]})
                
            days = 0
            
            temp_date = begin
            while(days < (dim - 1)):
                
                current_date = datetime.strptime(temp_date,'%Y-%m-%d')
                count = 1
                last_date = str(current_date - timedelta(days = count))
        
                while((not os.path.exists('option_data/option_'+ last_date[0:10] + '.csv')) and last_date[0:10] >= '2017-07-03'):
                    count = count + 1
                    last_date = str(current_date - timedelta(days = count))
                
                u_time = last_date[0:10]
                last_data = pd.read_csv('option_data/option_' + u_time + '.csv')
                
                
                changes_p = last_data['Change(P%)'].tolist()
                while '-' in changes_p:
                    changes_p.remove('-')
                    
                temp_changes_p_max = max([float(cp) for cp in changes_p])
                temp_changes_p_min = min([float(cp) for cp in changes_p])
                
                try:
                    last_index = last_data[(last_data['Option Code'] == code)].index.tolist()[0] 
                except:
                    break
                
                if last_data.loc[last_index,'Change(P%)'] == '-':
                    days = days + 1
                    continue
                else:
                    temp_P_change = float(last_data.loc[last_index,'Change(P%)'])
                
                if temp_P_change >= 0:
                    p_scale = abs(temp_changes_p_max)
                else:
                    p_scale = abs(temp_changes_p_min)
                
                if temp_changes_p_max == 0:
                    p_scale = abs(temp_changes_p_min)
                    P_data[code].append(temp_P_change / p_scale)
                
                elif temp_changes_p_min == 0:
                    p_scale = abs(temp_changes_p_max)
                    P_data[code].append(temp_P_change / p_scale)
                    
                else:
                    P_data[code].append(temp_P_change / p_scale)
    
                days = days + 1
                temp_date = u_time
                
                
            if len(P_data[code]) == (dim + 1):
                    
                if P_change >= P_benchmark:
                    P_data[code].append(1)
                else:
                    P_data[code].append(0)
            
            else:
                del P_data[code]         


        #cols = summary_data.keys()
        if C_data or P_data:
            C_data_pd = pd.DataFrame.from_dict(C_data, orient='index').T
            P_data_pd = pd.DataFrame.from_dict(P_data, orient='index').T
            one_data = pd.concat([C_data_pd, P_data_pd], axis = 1)
            
            month_data = pd.concat([month_data, one_data], axis = 1)
        
        begin_date = datetime.strptime(begin,'%Y-%m-%d')
        count = 1
        next_date = str(begin_date + timedelta(days = count))
        
        while((not os.path.exists('option_data/option_'+ next_date[0:10] + '.csv')) and next_date[0:10] < '2018-12-28'):
            count = count + 1
            next_date = str(begin_date + timedelta(days = count))
            
        begin = next_date[0:10]
#        print(begin)
        
    return month_data


if __name__=="__main__":  

    # 6 months for training, 1 months for testing

    # for 5 features
    begin_ends_5 = [
            ['2017-07-07','2017-07-31'],
            ['2017-08-04','2017-08-31'],
            ['2017-09-06','2017-10-03'],
            ['2017-10-10','2017-10-31'],
            ['2017-11-06','2017-11-30'],
            ['2017-12-06','2017-12-29'],
            ['2018-01-05','2018-01-31'],
            ['2018-02-06','2018-02-28'],
            ['2018-03-06','2018-03-29'],
            ['2018-04-09','2018-04-30'],
            ['2018-05-07','2018-05-31'],
            ['2018-06-06','2018-06-29'],
            ['2018-07-06','2018-07-31'],
            ['2018-08-06','2018-08-31'],
            ['2018-09-06','2018-09-28'],
            ['2018-10-05','2018-10-31'],
            ['2018-11-06','2018-11-30'],
            ]
    
    # for 10 features
    begin_ends_10 = [
            ['2017-07-14','2017-07-31'],
            ['2017-08-11','2017-08-31'],
            ['2017-09-13','2017-10-03'],
            ['2017-10-17','2017-10-31'],
            ['2017-11-13','2017-11-30'],
            ['2017-12-13','2017-12-29'],
            ['2018-01-12','2018-01-31'],
            ['2018-02-13','2018-02-28'],
            ['2018-03-13','2018-03-29'],
            ['2018-04-16','2018-04-30'],
            ['2018-05-14','2018-05-31'],
            ['2018-06-13','2018-06-29'],
            ['2018-07-13','2018-07-31'],
            ['2018-08-13','2018-08-31'],
            ['2018-09-13','2018-09-28'],
            ['2018-10-12','2018-10-31'],
            ['2018-11-13','2018-11-30'],
            ] 
    
    for i in range(len(begin_ends_5)):
        month_data = get_data(begin_ends_5[i][0], begin_ends_5[i][1], 5)
        
        file_name = 'train_data' + '/train_data_5d_' + begin_ends_5[i][0][0:7]
        month_data.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    