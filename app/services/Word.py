# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:31:31 2019

@author: ILENUCA
"""

from app import app

class Word:
    def __init__(self):
        self.regions = []
        self.N, self.S, self.W, self.E = 0, 0, 0, 0
        
    def add(self, region):
        self.regions.append(region)
        
    def setBoundaries(self):
        self.N = min([reg.N for reg in self.regions])
        self.S = max([reg.S for reg in self.regions])
        self.W = min([reg.W for reg in self.regions])
        self.E = max([reg.E for reg in self.regions])