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

#%%
def initialize_parameters_deep(layer_dims):

    parameters = {}
    L = len(layer_dims)

    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) * 0.01
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))
        
    return parameters

#%%
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


def L_model_forward(X, parameters, activation):

    caches = []
    A = X
    L = len(parameters) // 2

    for l in range(1, L):
        A_prev = A 
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], activation)
        caches.append(cache)

    AL, cache = linear_activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], "sigmoid")
    caches.append(cache)

    return AL, caches


#%%
def compute_cost(AL, Y):
    
    m = Y.shape[1]    
    cost = (-1/m) * (np.dot(Y,np.log(AL).T)+ np.dot(1-Y,np.log(1-AL).T))
    
    return cost


#%%
def linear_backward(dZ, cache):

    A_prev, W, b = cache
    m = A_prev.shape[1]

    dW = np.dot(dZ, A_prev.T)/m 
    db = np.sum(dZ, axis=1, keepdims=True)/m
    dA_prev = np.dot(W.T, dZ) 
    #dA is residual with respect to the activation (of the previous layer l-1), needs activation_backward further to chain

    return dA_prev, dW, db


def linear_activation_backward(dA, cache, activation):
    
    linear_cache, activation_cache = cache
    
    if activation == "relu":
        dZ = ut.relu_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)
        
    elif activation == "sigmoid":
        dZ = ut.sigmoid_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)
    
    return dA_prev, dW, db


def L_model_backward(AL, Y, caches):

    grads = {}
    L = len(caches)
    Y = Y.reshape(AL.shape)
    
    # output layer residual for cross-entropy
    dAL = - (np.divide(Y, AL) - np.divide(1 - Y, 1 - AL)) 
    current_cache = caches[L-1]
    grads["dA" + str(L-1)], grads["dW" + str(L)], grads["db" + str(L)] = linear_activation_backward(dAL, current_cache, "sigmoid")
    
    for l in reversed(range(L-1)):
        current_cache = caches[l]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(l+1)], current_cache, "relu")
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l + 1)] = dW_temp
        grads["db" + str(l + 1)] = db_temp

    return grads


#%%
def update_parameters(parameters, grads, learning_rate):

    L = len(parameters) // 2 # number of layers in the neural network

    for l in range(L):
        parameters["W" + str(l+1)] = parameters["W" + str(l+1)] - learning_rate*grads["dW" + str(l + 1)]
        parameters["b" + str(l+1)] = parameters["b" + str(l+1)] - learning_rate*grads["db" + str(l + 1)]

    return parameters



#%%
def predict(train_x, parameters, activation):
    
    m = train_x.shape[1]
    Y_prediction = np.zeros((1,m))
    AL, caches = L_model_forward(train_x, parameters, activation)

    for i in range(AL.shape[1]):
        
        if AL[0,i] > 0.5:
            Y_prediction[0,i] = 1
        else:
            Y_prediction[0,i] = 0

    return Y_prediction
