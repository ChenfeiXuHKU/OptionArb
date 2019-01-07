# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 14:20:54 2018

@author: chenf
"""
import numpy as np
import pandas as pd
import math
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb\utils")
import utils as ut    
    
def initialize_with_zeros(dim):
    w = np.zeros([dim,1])
    b = 0
    return w, b

def initialize_with_gaussian(dim):
    w =  np.random.randn(dim,1) * 0.01
    b = 0
    return w, b

def propagate(w, b, X, Y):

    m = X.shape[1]
    # FORWARD
    A = ut.sigmoid(np.dot(w.T,X)+b)                                   
    cost = (-1/m) * (np.dot(Y,np.log(A).T)+ np.dot(1-Y,np.log(1-A).T))
    # BACKWARD
    dw = (1/m) * np.dot(X,(A-Y).T)
    db = (1/m) * np.sum(A-Y)

    cost = np.squeeze(cost)
    grads = {"dw": dw,
             "db": db}
    
    return grads, cost


def optimize(w, b, X, Y, learning_rate):
    
    grads, cost = propagate(w, b, X, Y)

    dw = grads["dw"]
    db = grads["db"]
    
    w = w - learning_rate*dw
    b = b - learning_rate*db

    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, cost


def predict(w, b, X):

    m = X.shape[1]
    Y_prediction = np.zeros((1,m))
    w = w.reshape(X.shape[0], 1)
    A = ut.sigmoid(np.dot(w.T,X)+b)

    for i in range(A.shape[1]):
        
        if A[0,i] > 0.5:
            Y_prediction[0,i] = 1
        else:
            Y_prediction[0,i] = 0

    return Y_prediction


def LR_model(X_train, Y_train, learning_rate, w, b):

    parameters, grads, cost = optimize(w, b, X_train, Y_train, learning_rate)
    
    w = parameters["w"]
    b = parameters["b"]

    d = {"cost": cost,
         "w" : w, 
         "b" : b, }
    
    return d

path = '../train_data/'
names = ['2017-12','2018-01','2018-02','2018-03',\
         '2018-04','2018-05','2018-06','2018-07',\
         '2018-08','2018-09','2018-10','2018-11',]

dim = 5
iterations = 3000
learning_rate = 0.001

for name in names:
    train_set = pd.read_csv(path + 'train_data_' + str(dim) + 'd_' + name + '.csv')
    train_set = train_set.values
    w, b = initialize_with_zeros(dim*2)
    
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
                d = LR_model(train_x, train_y, learning_rate, w, b)
                w = d['w']
                b = d['b']
            else:
                start = batch_count * batch_size
                end = start + batch_size
                mini_train_set = train_set[:,random_index[start: end]]
                train_x = mini_train_set[1:11,:]
                train_y = mini_train_set[0:1,:]
                d = LR_model(train_x, train_y, learning_rate, w, b)
                w = d['w']
                b = d['b']
                batch_count = batch_count + 1
           
    train_x = train_set[1:11,:]
    train_y = train_set[0:1,:]       
    Y_prediction_train = predict(w, b, train_x) 
    print("train accuracy:{}%".format(100 - np.mean(np.abs(Y_prediction_train - train_y)) * 100))   
               
    w = d['w']
    b = np.reshape(np.array([d['b']]), (1,1))
        
    np.savetxt('./weights/w_' + str(learning_rate) + 'lr, ' + str(iterations) + 'iters, ' + str(dim) + 'f_' + name + '.txt', w, fmt='%0.8f')
    np.savetxt('./weights/b_' + str(learning_rate) + 'lr, ' + str(iterations) + 'iters, ' + str(dim) + 'f_' + name + '.txt', b, fmt='%0.8f')
    





