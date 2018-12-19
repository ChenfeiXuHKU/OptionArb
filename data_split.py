# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 19:28:21 2018

@author: chenf
"""
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import scipy
import os
#1. data process
path = '../train_data/'

name = 'train_data_5d_2017-12'
data_set = pd.read_csv(path + name + '.csv')

m = data_set.shape[1]   # 2000+

data_set_t = data_set.T

train_set_t = data_set_t.sample(frac = 0.7)
data_set_t = data_set_t.append(train_set_t)
test_set_t = data_set_t.drop_duplicates(keep=False)

train_set = train_set_t.T
test_set = test_set_t.T

#train_y = train_set.iloc[-1:]
#train_x = train_set.iloc[0:6]
#
#test_y = test_set.iloc[-1:]
#test_x = test_set.iloc[0:6]

file_name = path + 'train_data_5d_2017-12_1'
train_set.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)

file_name = path + 'test_data_5d_2017-12_1'
test_set.to_csv(file_name + '.csv', sep=',', na_rep='N/A', index=False)
























