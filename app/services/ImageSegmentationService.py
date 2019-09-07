# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 17:22:39 2019

@author: ILENUCA
"""

import numpy as np
import cv2
import sys
import time

minimizer = lambda x: min(x)

class Region:
    def __init__(self, h, w, label):
        self.label = label
        self.h = h
        self.w = w
        
        self.mask = np.zeros([h,w],dtype=np.uint8)
        self.mask.fill(255)
        self.area = 0
        
        self.N = h #smallest row in the list of points
        self.S = 0 #biggestt row
        self.W = w #smallest column in the list of points
        self.E = 0 #biggest column
        
    def addPoint(self, x, y):
        self.mask.itemset((x,y),0);
        self.area += 1
        
        self.N = min(self.N, x)
        self.S = max(self.S, x)
        self.W = min(self.W, y)
        self.E = max(self.E, y)
        
    def cropImg(self):        
        self.cropped = self.mask[self.N:self.S+1, self.W:self.E+1]
        height, width = self.cropped.shape
        
        import scipy.misc
        scipy.misc.imsave('cropped/' + str(self.area) + '_' + str(self.label) + '.png', self.cropped)
        print(str(self.area) + '_' + str(self.label) + '.png', end=', ')

class CCL:
    def __init__(self, filename):
        self.image = cv2.imread(filename)        
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.foreground = [level < 124 for level in image]
        self.h, self.w = image.shape
        self.labels = [[-1 for i in range(0,self.w)] for j in range(0, self.h)]
        
        self.eqClasses = []
        self.currLabel = 0;
        self.x, self.y = 0, 0 #initial point from where we start traversing the image
        
        timeElapsed = time.time()
        for i in range(self.h):
            for j in range(self.w):
                self.x = i
                self.y = j
                if self.foreground[self.x][self.y]:
                    self.labelPoint()
        timeElapsed = time.time() - timeElapsed
        print('Label Points - ', timeElapsed)
        self.relabelPoints()
    
    def labelPoint(self):
        # print('#labelPoint')
        nbrLbls = set()
        
        if self.y > 0:
            label = self.labels[self.x][self.y-1]
            nbrLbls.add(label)
        if self.x > 0:
            label = self.labels[self.x-1][self.y]
            nbrLbls.add(label)
            if self.y > 0:
                label = self.labels[self.x-1][self.y-1]
                nbrLbls.add(label)
            if self.y < self.w-1:
                label = self.labels[self.x-1][self.y+1]
                nbrLbls.add(label)
        
        nbrLbls = {label for label in nbrLbls if label >= 0}
        if len(nbrLbls) > 0:
            self.labels[self.x][self.y] = next(iter(nbrLbls))
            for i in nbrLbls:
                self.eqClasses[i] = self.eqClasses[i].union(nbrLbls)
        else:
            self.labels[self.x][self.y] = self.currLabel
            self.eqClasses.insert(self.currLabel, {self.currLabel});
            self.currLabel = self.currLabel + 1

    def relabelPoints(self):
        timeElapsed = time.time()
        self.eqClasses = list(map(minimizer, self.eqClasses))
        self.eqClasses.append(-1)
        
        self.regions = [Region(self.h, self.w, i) for i in set(self.eqClasses)]
        regLbls = [reg.label for reg in self.regions]
        
        self.labels = [[self.regions[regLbls.index(self.eqClasses[self.labels[i][j]])].addPoint(i,j) 
                        for j in range(self.w) if self.labels[i][j] != -1] for i in range(self.h)]
        
        self.regions = [reg for reg in self.regions if reg.area > 10]
        
        timeElapsed = time.time() - timeElapsed
        print('Relabel Points - ', timeElapsed)
        
#        self.saveRegions()
                
    def saveRegions(self):
        mean = sum(self.regions)/len(self.regions)
        errLow = int(mean - mean/2)
        
        for region in self.regions:
            if region.area > errLow:
                region.cropImg()