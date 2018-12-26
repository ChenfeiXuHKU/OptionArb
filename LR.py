# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 14:20:54 2018

@author: chenf
"""
import numpy as np
import pandas as pd
import utils as ut

path = './train_data/'
savepath = './LR/'
tid = 1
name = '2017-12'
train_set = pd.read_csv(path + 'train_data_5d_' + name + '_' + str(tid) + '.csv')
test_set = pd.read_csv(path + 'test_data_5d_' + name + '_' + str(tid) + '.csv')

train_x = train_set.iloc[1:11].values
train_y = train_set.iloc[0:1].values

test_x = test_set.iloc[1:11].values
test_y = test_set.iloc[0:1].values


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


def optimize(w, b, X, Y, num_iterations, learning_rate, print_cost, X_test, Y_test):
    
    costs = []
    test_costs=[]
    
    for i in range(num_iterations):
        
        grads, cost = propagate(w, b, X, Y)

        dw = grads["dw"]
        db = grads["db"]

        w = w - learning_rate*dw
        b = b - learning_rate*db
        
        if i % 100 == 0:
            costs.append(cost)
            m = X_test.shape[1]
            test_A = ut.sigmoid(np.dot(w.T,X_test)+b)                                   
            test_cost = (-1/m) * (np.dot(Y_test,np.log(test_A).T)+ np.dot(1-Y_test,np.log(1-test_A).T))
            test_costs.append(test_cost)

        if print_cost and i % 100 == 0:
            print ("Cost after iteration %i: %f" %(i, cost))
            print ("Test Cost after iteration %i: %f" %(i, test_cost))

    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, costs, test_costs


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


def LR_model(X_train, Y_train, X_test, Y_test, num_iterations, learning_rate, print_cost):

    dim = X_train.shape[0]
    w, b = initialize_with_zeros(dim)
    
    parameters, grads, costs, test_costs = optimize(w, b, X_train, Y_train, num_iterations, \
                                                    learning_rate, print_cost, X_test, Y_test)
    
    w = parameters["w"]
    b = parameters["b"]
    
    Y_prediction_test = predict(w, b, X_test)
    Y_prediction_train = predict(w, b, X_train)
    
    print("train accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_train - Y_train)) * 100))
    print("test accuracy: {} %".format(100 - np.mean(np.abs(Y_prediction_test - Y_test)) * 100))

    
    d = {"costs": costs,
         "Y_prediction_test": Y_prediction_test, 
         "Y_prediction_train" : Y_prediction_train, 
         "w" : w, 
         "b" : b, 
         "learning_rate" : learning_rate,
         "num_iterations": num_iterations}
    
    return d

d = LR_model(train_x, train_y, test_x, test_y, 2000, 0.5, False)
w = d['w']
b = np.reshape(np.array([d['b']]), (1,1))

np.savetxt(savepath + 'w_' + name + '_' + str(tid) + '.txt', w, fmt='%0.8f')
np.savetxt(savepath + 'b_' + name + '_' + str(tid) + '.txt', b, fmt='%0.8f')





