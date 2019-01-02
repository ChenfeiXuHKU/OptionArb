# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 13:53:41 2018

@author: chenf
"""
import sklearn
import sklearn.datasets
import sklearn.linear_model
import numpy as np
import pandas as pd

path = './train_data/'

tid = 1

train_set = pd.read_csv(path + 'train_data_5d_2017-12_' + str(tid) + '.csv')
test_set = pd.read_csv(path + 'test_data_5d_2017-12_' + str(tid) + '.csv')

train_x = train_set.iloc[1:11].values
train_y = train_set.iloc[0:1].values

test_x = test_set.iloc[1:11].values
test_y = test_set.iloc[0:1].values

clf = sklearn.linear_model.LogisticRegressionCV();
clf.fit(train_x.T, train_y.T)

LR_predictions = clf.predict(train_x.T)
print ('Accuracy of logistic regression: %d ' % float((np.dot(train_y,LR_predictions) + np.dot(1-train_y,1-LR_predictions))/float(train_y.size)*100) +
       '% ' + "(percentage of correctly labelled datapoints)")

