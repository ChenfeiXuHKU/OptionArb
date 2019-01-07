# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 21:32:36 2019

@author: chenf
"""
import numpy as np
import pandas as pd
import math
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb\utils")
import nn_modules as nnm

def L_layer_model(X, Y, layers_dims, activation, parameters, learning_rate):

    AL, caches = nnm.L_model_forward(X, parameters, activation)

    grads = nnm.L_model_backward(AL, Y, caches)
    
    parameters = nnm.update_parameters(parameters, grads, learning_rate)

    return parameters

#%%
path = '../train_data/'
names = ['2017-12','2018-01','2018-02','2018-03',\
         '2018-04','2018-05','2018-06','2018-07',\
         '2018-08','2018-09','2018-10','2018-11',]
dim = 5
layers_dims = [dim*2, dim, 1] #  2-layer model
#layers_dims = [dim*2, dim, 2, 1] #  3-layer model

iterations = 1000
learning_rate = 0.001
activation = 'relu'

for name in names:
    train_set = pd.read_csv(path + 'train_data_' + str(dim) + 'd_' + name + '.csv')
    train_set = train_set.values
    parameters = nnm.initialize_parameters_deep(layers_dims)

    batch_size = 100
    for i in range(iterations):
        random_index = np.random.permutation(train_set.shape[1]).tolist()       
        batch_count = 0
        batches = math.ceil(train_set.shape[1] / batch_size)
        for j in range(batches):
            if batch_count * batch_size + batch_size > train_set.shape[1]:
                mini_train_set = train_set[:,random_index[batch_count * batch_size:]]
                train_x = mini_train_set[1:11,:]
                train_y = mini_train_set[0:1,:]
                parameters = L_layer_model(train_x, train_y, layers_dims, activation, parameters, learning_rate)
            else:
                start = batch_count * batch_size
                end = start + batch_size
                mini_train_set = train_set[:,random_index[start: end]]
                train_x = mini_train_set[1:11,:]
                train_y = mini_train_set[0:1,:]
                parameters = L_layer_model(train_x, train_y, layers_dims, activation, parameters, learning_rate)
                batch_count = batch_count + 1
           
    train_x = train_set[1:11,:]
    train_y = train_set[0:1,:]       
    Y_prediction_train = nnm.predict(train_x, parameters, activation)
    print("train accuracy:{}%".format(100 - np.mean(np.abs(Y_prediction_train - train_y)) * 100))   
    
    #save
    L = len(parameters) // 2
    for l in range(L):
        w = parameters["W" + str(l+1)]
        b = parameters["b" + str(l+1)]        
        np.savetxt('./weights/w_' + str(L) + 'l_' + str(l+1) + '_' + str(learning_rate) + \
                   'lr_' + activation + '_' + str(iterations) + 'iters_' + str(dim) + 'f_' + name + '.txt', w, fmt='%0.8f')
        np.savetxt('./weights/b_' + str(L) + 'l_' + str(l+1) + '_' + str(learning_rate) + \
                   'lr_' + activation + '_' + str(iterations) + 'iters_' + str(dim) + 'f_' + name + '.txt', b, fmt='%0.8f')







