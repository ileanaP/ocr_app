# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 17:22:39 2019

@author: ILENUCA
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 13:32:52 2019




@author: ILENUCA
"""

import numpy as np
import cv2
import sys
import time
import statistics
import scipy.misc

minimizer = lambda x: min(x)

class Region:
    def __init__(self, h, w, label):
        self.label = label
        self.imgH = h
        self.imgW = w
        self.h = 0
        self.w = 0
        
        self.bigOutlier = False   # used to determine wether a region is too big, or has more letters
        self.smallOutlier = False # same as above, only for small regions
        
        self.area = 0
        
        self.N = h #smallest row in the list of points
        self.S = 0 #biggestt row
        self.W = w #smallest column in the list of points
        self.E = 0 #biggest column
        
    def addPoint(self, x, y):
#        self.mask.itemset((x,y),0);
        self.area += 1
        
        self.N = min(self.N, x)
        self.S = max(self.S, x)
        self.W = min(self.W, y)
        self.E = max(self.E, y)
    
    def isMargin(self):
        return self.N == 0 or self.S == self.imgH - 1 or self.W == 0 or self.E == self.imgW - 1
    
    def isEligible(self):
        returnValue = 1
        
        returnValue = returnValue and not self.area == 0
        returnValue = returnValue and not self.isMargin() # scot outlierii mari si pixeli razleti
        
        return returnValue
        
    def calculateRatio(self):
        self.h = self.S - self.N
        self.w = self.E - self.W
        
        self.ratio = float(self.w)/float(self.h)
        
        return self.ratio
        
    def cropImg(self, mask):        
        self.cropped = mask[self.N:self.S+1, self.W:self.E+1]
        self.cropped = [[255 if value == self.label else 0 for value in row ] for row in self.cropped]
        self.cropped = np.asarray(self.cropped, dtype=np.int8)

        height, width = self.cropped.shape
        
        fileName = str(self.area) + '_' + str(self.label)
        
        if self.bigOutlier:
            fileName = fileName + "_bigoutlier"
        
        if self.smallOutlier:
            fileName = fileName + "_smalloutlier"

        if self.isMargin():
            fileName = fileName + "_margin"
                
        fileName = fileName + ".png"
            
        scipy.misc.imsave('cropped/' + fileName, self.cropped)
#        print(str(self.area) + '_' + str(self.label) + '.png', end=', ')

class CCL:
    def __init__(self, filename):
        self.iter = 0
        self.image = cv2.imread(filename)        
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        self.foreground = [level < 124 for level in self.image]
        
        self.h, self.w = self.image.shape
        self.labels = [[-1 for i in range(0,self.w)] for j in range(0, self.h)]
        
        self.mask = np.zeros([self.h,self.w],dtype=np.uint32)
        self.mask.fill(255)
        
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
        self.findOutliers()
        self.saveRegions()
    
    def labelPoint(self):
        nbrLbls = set()
        
        for x in range(self.x-2, self.x+1):
            for y in range(self.y-2, self.y+3):
                if not (x == self.x and y == self.y):
                    if x > -1 and y > -1 and y < self.w:
                        label = self.labels[x][y]
                        nbrLbls.add(label)

        nbrLbls = {label for label in nbrLbls if label >= 0}
        if len(nbrLbls) > 0:
            self.labels[self.x][self.y] = next(iter(nbrLbls))
            
            neighborSet = set()
            for i in nbrLbls:
                neighborSet = neighborSet.union(self.eqClasses[i])
            
            neighborSet = neighborSet.union(nbrLbls)
            
            for i in neighborSet:
                self.eqClasses[i] = neighborSet
        else:
            self.labels[self.x][self.y] = self.currLabel
            self.eqClasses.insert(self.currLabel, {self.currLabel});
            self.currLabel = self.currLabel + 1

    def relabelPoints(self):
        timeElapsed = time.time()
        
        self.eqClassesHat = list(map(minimizer, self.eqClasses))
        self.eqClassesHatSingles = list(dict.fromkeys(self.eqClassesHat))
        
        self.eqClassesHat.append(-1)
        self.eqClassesHatSingles.append(-1)
        
        self.regions = [Region(self.h, self.w, i) for i in self.eqClassesHatSingles]
        
        self.labels = [[self.addPoint(i,j) 
                        for j in range(self.w) if self.labels[i][j] != -1] for i in range(self.h)]
        
#        self.regions = [reg for reg in self.regions if reg.area > 0]
        self.regions = [reg for reg in self.regions if reg.isEligible()]
        
        timeElapsed = time.time() - timeElapsed
        print('Relabel Points - ', timeElapsed)
        
    def findOutliers(self):        
        # vreau sa scot margins, si regions cu aria 1
        # vreau sa gasesc outliers in functie de area (standard deviation)
        # dintre outlierii mici, vreau sa gasesc semne de punctuatie, puncte pe i/j, etc
        # dintre outlierii mari, vreau sa gasesc daca sunt mai multe litere in ei, si sa ii sparg
        # --- in functie de ratio a elementelor care nu sunt outlieri (SD a ratio)
        # daca dintre outlierii mari sunt linii orizontale __ sau verticale | care nu sunt margini? 
        # --- scot liniile | si liniile __ devin "_ _ _ _" in textul final (SD a ratio)
        
        
        regionAreas = [reg.area for reg in self.regions]
        
        areaMean = int(sum(regionAreas) / len(regionAreas))
        areaStDev = statistics.pstdev(regionAreas) # standard deviation
        
        print('area mean: ', areaMean)
        print('area st dev: ', areaStDev)
        
        for reg in self.regions:
            if reg.area > areaMean + areaStDev:
                reg.bigOutlier = True
            if reg.area < areaMean - areaStDev:
                reg.smallOutlier = True
        
    def addPoint(self, i, j):        
        currLabelHat = self.eqClassesHat[self.labels[i][j]]
        currLabelRegionIndex = self.eqClassesHatSingles.index(currLabelHat)
        
        self.regions[currLabelRegionIndex].addPoint(i,j)
        
        self.mask.itemset((i,j),currLabelHat)
                
    def saveRegions(self):
#        mean = sum(self.regions)/len(self.regions)
#        errLow = int(mean - mean/2)
        
#        print(self.mask)
#        sys.exit()
        
        for region in self.regions:
#            if region.area > errLow:
            region.cropImg(self.mask)
                
thisCCL = CCL("ccl_image_01.jpg")