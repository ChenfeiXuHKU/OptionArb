# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 19:28:21 2018
split data if needed
@author: chenf
"""
import pandas as pd

path = '../train_data/'

names = ['2017-12','2018-01','2018-02','2018-03',\
         '2018-04','2018-05','2018-06','2018-07',\
         '2018-08','2018-09','2018-10','2018-11',]
numbers = [5,10]
split_ratio = 0.7

for na in names:
    for nu in numbers:
        name = 'train_data_' + str(nu) + 'd_' + na
        data_set = pd.read_csv(path + name + '.csv')
        
        m = data_set.shape[1]
        
        data_set_t = data_set.T
        
        train_set_t = data_set_t.sample(frac = split_ratio)
        data_set_t = data_set_t.append(train_set_t)
        test_set_t = data_set_t.drop_duplicates(keep=False)
        
        train_set = train_set_t.T
        test_set = test_set_t.T   
        
        file_name = path + 'split_train_data_' + str(nu) + 'd_' + na
        train_set.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
        
        file_name = path + 'split_test_data_' + str(nu) + 'd_' + na
        test_set.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)




