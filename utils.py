# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 15:12:51 2018

@author: chenf
"""
import numpy as np

def sigmoid(z):

    s = 1/(1 + 1/np.exp(z))

    return s



