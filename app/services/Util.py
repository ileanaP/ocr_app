# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:34:56 2019

@author: ILENUCA
"""

from app import app
import statistics

class Util:
    minimizer = lambda x: min(x)
    
    @staticmethod
    def getMeanStDev(elems):
        mean = sum(elems) / len(elems)
        stDev = statistics.pstdev(elems) # standard deviation
        
        return { 'm': mean, 'sd': stDev }