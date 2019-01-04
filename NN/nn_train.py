# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 13:00:36 2019

@author: chenf
"""
import numpy as np
import pandas as pd
import math
import sys
sys.path.append(r"C:\Users\chenf\Desktop\GITS\OptionArb\utils")
import utils as ut    

structure = [10, 5, 1]

def initialize_parameters_deep(layer_dims):

    parameters = {}
    L = len(layer_dims)

    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) * 0.01
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))
        
    return parameters

def linear_forward(A, W, b):
    
    Z = np.dot(W,A)+b
    cache = (A, W, b)
    
    return Z, cache


def linear_activation_forward(A_prev, W, b, activation):
    
    if activation == "sigmoid":
        Z, linear_cache = linear_forward(A_prev,W,b)
        A = ut.sigmoid(Z)
    
    elif activation == "relu":
        Z, linear_cache = linear_forward(A_prev,W,b)
        A = ut.relu(Z)
    
    cache = (linear_cache, Z)

    return A, cache


def L_model_forward(X, parameters):
    """
    Implement forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID computation
    
    Arguments:
    X -- data, numpy array of shape (input size, number of examples)
    parameters -- output of initialize_parameters_deep()
    
    Returns:
    AL -- last post-activation value
    caches -- list of caches containing:
                every cache of linear_activation_forward() (there are L-1 of them, indexed from 0 to L-1)
    """

    caches = []
    A = X
    L = len(parameters) // 2                  # number of layers in the neural network
    
    # Implement [LINEAR -> RELU]*(L-1). Add "cache" to the "caches" list.
    for l in range(1, L):
        A_prev = A 
        ### START CODE HERE ### (≈ 2 lines of code)
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], "relu")
        caches.append(cache)
        ### END CODE HERE ###
    
    # Implement LINEAR -> SIGMOID. Add "cache" to the "caches" list.
    ### START CODE HERE ### (≈ 2 lines of code)
    AL, cache = linear_activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], "sigmoid")
    caches.append(cache)
    ### END CODE HERE ###
    
    assert(AL.shape == (1,X.shape[1]))
            
    return AL, caches







def compute_cost(A2, Y, parameters):
    
    m = Y.shape[1]    
    cost = (-1/m) * (np.dot(Y,np.log(A2).T)+ np.dot(1-Y,np.log(1-A2).T))
    
    return cost

def backward_propagation(parameters, cache, X, Y):

    m = X.shape[1]
    
    W1 = parameters['W1']
    W2 = parameters['W2']

    A1 = cache['A1']
    A2 = cache['A2']
    
    dZ2 = A2 - Y #1xm
    dW2 = np.dot(dZ2, A1.T)/m 
    db2 = np.sum(dZ2, axis=1, keepdims=True)/m
    dZ1 = np.dot(W2.T, dZ2)*(1 - np.power(A1, 2))     #4xm
    dW1 = np.dot(dZ1, X.T)/m
    db1 = np.sum(dZ1, axis=1, keepdims=True)/m
    
    grads = {"dW1": dW1,
             "db1": db1,
             "dW2": dW2,
             "db2": db2}
    
    return grads


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
number = 5
iterations = 1000
learning_rate = 0.1

for name in names:
    train_set = pd.read_csv(path + 'train_data_' + str(number) + 'd_' + name + '.csv')
    train_set = train_set.values
    dim = train_set.shape[0] - 1
    w, b = initialize_with_zeros(dim)
    
#    batch_size = 50
    batch_size = train_set.shape[1]
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
        
    np.savetxt('w_batch_' + str(number) + '_' + name + '.txt', w, fmt='%0.8f')
    np.savetxt('b_batch_'+ str(number) + '_' + name + '.txt', b, fmt='%0.8f')
