# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:37:00 2019

@author: ILENUCA
"""

from app import app
import scipy.misc
import imageio
import numpy as np
import math
import os
import sys
import time

class Region:
    areaMSD    = 0
    ratioMSD   = 0
    densityMSD = 0
    def __init__(self, h, w, label):
        self.label = label
        self.imgH = h
        self.imgW = w
        
        self.h, self.w, self.area, self.ratio, self.density, self.line = 0, 0, 0, 0, 0, 0
        
        self.out = {
                    "areaOver"    : False, "areaUnder"    : False, # used to determine wether a region is too big, or has more letters
                    "ratioOver"   : False, "ratioUnder"   : False, # same as above, only for small regions
                    "densityOver" : False, "densityUnder" : False, 
                    "dot"         : False
                   }
        
        self.N = h # NORTH - smallest row in the list of points
        self.S = 0 # SOUTH - biggestt row
        self.W = w # WEST  - smallest column in the list of points
        self.E = 0 # EAST  - biggest column
     
    @classmethod
    def setMetric(cls, area, ratio, density):
        cls.areaMSD = area
        cls.ratioMSD = ratio
        cls.densityMSD = density
        
    def addPoint(self, x, y):
        self.area += 1
        
        self.N = min(self.N, x)
        self.S = max(self.S, x)
        self.W = min(self.W, y)
        self.E = max(self.E, y)
        
    def getWest(self):
        return self.W
    
    def isMargin(self):
        return self.N == 0 or self.S == self.imgH - 1 or self.W == 0 or self.E == self.imgW - 1
    
    def isEligible(self):
        returnValue = 1
        
        returnValue = returnValue and not self.area < 7
        returnValue = returnValue and not self.isMargin() # scot outlierii mari si pixeli razleti
        
#        if self.label == 34:
#            self.printCoords()
#            print(returnValue)
#            print(self.area)
#            if self.area == 0:
#                sys.exit()
        
        return returnValue
        
    def calculateRatio(self):
        self.h = self.S - self.N + 1
        self.w = self.E - self.W + 1

        self.ratio = float(self.w)/float(self.h)
        
        return self.ratio
    
    def calculateDensity(self):
        
        if self.area != 0:
            totalArea = (self.S - self.N) * (self.E - self.W)
            self.density = self.area/totalArea if totalArea != 0 else 0
            
        return self.density
    
    def join(self, reg):        
        self.area = self.area + reg.area
        
        self.N = min(self.N, reg.N)
        self.S = max(self.S, reg.S)
        self.W = min(self.W, reg.W)
        self.E = max(self.E, reg.E)
        
        reg.wipe()
        
        self.setOutliers()
        reg.setOutliers()
        
    def wipe(self):
        self.area = 0
        
        self.N, self.S, self.W, self.E = 0, 0, 0, 0
        
    def setOutliers(self):        
        self.calculateRatio()
        
        self.out['areaOver']     = True if self.area    > self.areaMSD['m']    + self.areaMSD['sd']    else False
        self.out['areaUnder']    = True if self.area    < self.areaMSD['m']    - self.areaMSD['sd']    else False
        self.out['ratioOver']    = True if self.ratio   > self.ratioMSD['m']   + self.ratioMSD['sd']   else False
        self.out['ratioUnder']   = True if self.ratio   < self.ratioMSD['m']   - self.ratioMSD['sd']   else False
        self.out['densityOver']  = True if self.density > self.densityMSD['m'] + self.densityMSD['sd'] else False
        self.out['densityUnder'] = True if self.density < self.densityMSD['m'] - self.densityMSD['sd'] else False
            
        self.out['dot'] = False
        
        if self.ratio >= 0.6 and self.ratio <= 1.4:
            if self.out['areaUnder'] or self.out['densityOver']: # TO DO - am adaugat aici "densityOver"
                self.out['dot'] = True                           # pentru a rezolva ca in _02 nu se grupau ":" pentru ca unul din ei
                                                                 # nu era dot - modifica asta ceva la rezultatele de pana acum?
                                                                 # (de ex. pt ",")
            
    def getSplitRegions(self, meanWidth, mask, currLabel):
        
        regions = []
        
        if self.out["ratioOver"] and not (self.out["areaUnder"] or self.out["densityOver"]):
            nrSplit = int(round(self.w/meanWidth))
            nrSplit = float((self.w - (nrSplit-1)*2))/meanWidth
            nrSplit = math.floor(nrSplit) # floor - pentru a nu lua mai multe elems decat e necesar (cum ar putea fi cazul la "ceil")
            
            if nrSplit > 1:
                regions, currLabel = self.split(nrSplit, mask, currLabel)
                
        return regions, currLabel
    
    def isNear(self, reg):
        if self.W >= reg.E and self.W <= reg.E + (reg.E - reg.W):
            return True
        else:
            return False
    
    def printCoords(self):
        print("N: ", self.N)
        print("S: ", self.S)
        print("W: ", self.W)
        print("E: ", self.E)
        
    def split(self, nrSplit, mask, lastLabel):
        newRegions = []
        splitWidth = int(self.w/nrSplit)
        
        for i in range(nrSplit):
            currLabel = lastLabel + i
            region = Region(self.imgH, self.imgW, currLabel)
            for y in range(self.W + splitWidth * i, self.W + splitWidth *(i+1)):
                for x in range(self.N, self.S):
                    if mask[x][y] == self.label:
                        region.addPoint(x,y)
                        mask.itemset((x,y), currLabel)
                        
            newRegions.append(region)
            
        return newRegions, currLabel + 1

    def cropImg(self, line, char, mask):        
        self.cropped = mask[self.N:self.S+1, self.W:self.E+1]
        self.cropped = [[0 if value == self.label else 254 for value in row ] for row in self.cropped]
        
        self.cropped = np.asarray(self.cropped, dtype = np.uint8)
        
        fileName = str(line+1) + "_" + str(char+1) + "_" +str(self.area) + '_' + str(self.label) + ".png"
#        fileName = fileName + "_N" + str(self.N) + "S" + str(self.S) + "W" + str(self.W) + "E" + str(self.E) + ".png"
        
        croppedFilePath = os.path.join(app.config['CROPPED_FOLDER'], fileName)
        imageio.imwrite(croppedFilePath, self.cropped)
        
        return fileName
        
        