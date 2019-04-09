# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:29:44 2019

@author: chenf
"""
from __future__ import division
from datetime import datetime 
from time import sleep
from collections import OrderedDict
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
import quandl
quandl.ApiConfig.api_key = 'FxbKCf83-WeNae8uyxQg'
from lxml import html  
import requests


def price_option(S, K, r, q, sigma, T, t_o):
    
    if sigma > 0 and T > 0:
        d1 = (math.log(S/K) + (r - q + 0.5*(sigma**2))*T)/(sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        
        if t_o == 0:
            C = S*math.exp(-1*q*(T))*norm.cdf(d1) - K*math.exp(-1*r*(T))*norm.cdf(d2)
            return C,d1,d2
        else:
            P = K*math.exp(-1*r*(T))*norm.cdf(-1*d2) - S*math.exp(-1*q*(T))*norm.cdf(-1*d1)
            return P
    else:
        return -1
    
C,D,D1=price_option(89.9, 90, 0.0015, 0.0424, 0.22, 0.0411, 0)   
    
    
    