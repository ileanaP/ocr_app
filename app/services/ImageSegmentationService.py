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

imageToRead = "ccl_image_03.jpg"

import numpy as np
import cv2
import time
import math
import Util
import Line
import Region

class ImageSegmentationService:
    def __init__(self, filename):
        self.iter = 0
        self.image = cv2.imread(filename)        
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        self.foreground = [level < 124 for level in self.image]
        
        self.h, self.w = self.image.shape
#        self.labels = [[-1 for i in range(0,self.w)] for j in range(0, self.h)]
        
        self.labels = np.zeros([self.h,self.w],dtype=np.int32)
        self.labels.fill(-1)
        
        self.mask = np.zeros([self.h,self.w],dtype=np.int32)
        self.mask.fill(-1)
        
        self.eqClasses = []
        self.etiquete = []
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
        print('# labelPoints() - ', timeElapsed)
        
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
        
        self.eqClassesHat = list(map(Util.minimizer, self.eqClasses))
        self.eqClassesHatSingles = list(dict.fromkeys(self.eqClassesHat))
        
        self.eqClassesHat.append(-1)
        self.eqClassesHatSingles.append(-1)
        
        self.regions = [Region(self.h, self.w, i) for i in self.eqClassesHatSingles]
        
        self.labels = [[self.addPoint(i,j) 
                        for j in range(self.w) if self.labels[i][j] != -1] for i in range(self.h)]

        self.removeNotEligible()
        
        timeElapsed = time.time() - timeElapsed
        print('# relabelPoints() - ', timeElapsed)
        
    def findOutliers(self):
        self.setMetric()
        
        for reg in self.regions:            
            if reg.out["dot"]:
                self.tryFindRegionParent(reg)
        
        self.removeNotEligible()
        
        self.setMetric()
        
        self.setLines()
        self.otherThanSetLines()
        self.show()
        # TO DO - pentru 02, ia "Birne" ca un sg. cuvant
        
    def removeNotEligible(self):
        regionsToRemove = [reg for reg in self.regions if not reg.isEligible()]
        
        for reg in regionsToRemove:
            self.mask[self.mask == reg.label] = -1
            self.regions.remove(reg)
        
    def setLines(self):
        currLine = 1
       
        for reg in self.regions:
            if reg.line == 0:
                neighbors = self.getNeighborRegions(reg)
                
                neighborLines = [neighbor.line for neighbor in neighbors if neighbor.line != 0]
                
                if len(neighborLines) == 0:
                    for neighbor in neighbors:
                        neighbor.line = currLine
                    reg.line = currLine
                    currLine = currLine + 1
                else:
                    reg.line = min(neighborLines)
                    for neighbor in neighbors:
                        neighbor.line = reg.line
                        
        allLines = [reg.line for reg in self.regions]
        allLines = np.unique(np.asarray(allLines))
        
        self.lines = [Line([reg for reg in self.regions if reg.line == i]) for i in allLines]
        
    def show(self):
        lineThickness = 2
        # SHOW LINES
        tempimage = cv2.imread(imageToRead)
        
        for line in self.lines:
            if line.symbol:
                lineColor = (255,255,0)
            else:
                lineColor = (125,125,125)

            cv2.line(tempimage, (0, line.N-1), (self.w, line.N-1), lineColor, lineThickness)
            cv2.line(tempimage, (0, line.S+2), (self.w, line.S+2), lineColor, lineThickness)
        
        # SHOW WORDS
        for line in self.lines:
            for word in line.words:                    
                tempimage = cv2.rectangle(tempimage,(word.W-1,word.N-1),(word.E+2,word.S+2),(255,0,255),lineThickness)
                
        cv2.imshow('image',tempimage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imwrite('scannedimage_words.jpg', tempimage)
        
        # SHOW LINE BOUNDARIES
#        tempimage = cv2.imread(imageToRead)
#        for line in self.lines:            
#            tmpColor = (0,0,255)
#            if line.symbol:
#                tmpColor = (125,125,125)
#            tempimage = cv2.rectangle(tempimage,(line.W,line.N),(line.E,line.S),tmpColor,2)
#            
#        tempimage = cv2.rectangle(tempimage,(Line.W,Line.N),(Line.E,Line.S),(255,0,0),3)
#            
#        cv2.imshow('image',tempimage)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()
#
#        cv2.imwrite('scannedimage_boundaries.jpg', tempimage)
        
        #  tempimage = cv2.rectangle(tempimage,(reg.W,reg.N),(reg.E,reg.S),(0,0,255),2) # ex. de aplicare a metodei "rectangle"
        
        
    def otherThanSetLines(self):        
        #get ratio of elemes not symbols and not area under or over
        normalRatios = [reg.ratio for reg in self.regions 
                            if not (reg.out["densityOver"] or reg.out["areaOver"] or reg.out["areaUnder"])]
        normalRatio = Util.getMeanStDev(normalRatios)
        
        for line in self.lines:
            widths = [reg.w for reg in line.regions]
            width = Util.getMeanStDev(widths)
            
            meanWidth = math.floor(normalRatio['m'] * width['m']) # floor - pentru a "prinde" cat mai multe elemente 
            
            regionsToAdd, regionsToRemove = [], []
            
            #segment regions wich may contain more than one letter :D            
            for reg in line.regions:
                regions, label = reg.getSplitRegions(meanWidth, self.mask, self.currLabel)
                
                if label > self.currLabel:
                    regionsToAdd.append(regions)
                    regionsToRemove.append(reg)
                        
            for cluster in regionsToAdd:
                for reg in cluster:
                    line.regions.append(reg)

                line.regions = [reg for reg in line.regions if reg not in regionsToRemove]
        
        Line.setBoundaries(self.lines)
        Line.setIsSymbol(self.lines)
        
    def getNeighborRegions(self, reg):
        
        regionMiddle = reg.N + int((reg.S - reg.N)/2)
        
        neighborLabels = self.mask[regionMiddle:regionMiddle+1,]
        
        neighbors = [r for r in self.regions if (r.label in neighborLabels and r.label != -1 )]        

        return neighbors

        
    def tryFindRegionParent(self, reg):        
        if reg.out["dot"]:
            areaH = reg.h * 3 # sa verific si doua in sus, mai bine, mai intai xD
            
            # get 3h*w rectangle that starts 1h below dot "reg" region
            cropped = self.mask[reg.N + reg.h:reg.N+areaH+1, reg.W:reg.E+1]                
            
            # find unique labels corresponding to above region
            croppedLabels = np.unique(np.asarray(cropped))
            
            # remove default label (-1)
            croppedLabels = [tmp for tmp in croppedLabels if tmp != -1]
            
            # if 1 unique label was found, it is a good "parent" candidate for the dot, we will join the regions
            # if more than one or none is found, the result is inconclusive, do nothing
            if len(croppedLabels) == 1:
                croppedLabel = croppedLabels[0]
                desiredRegion = [x for x in self.regions if x.label == croppedLabel][0]
                    
                self.mask[self.mask == reg.label] = croppedLabel
                desiredRegion.join(reg)
                
    def setMetric(self):
        regionAreas = [reg.area for reg in self.regions]
        self.area = Util.getMeanStDev(regionAreas) # get area mean (M) and area standard deviation (SD)
        
        regionRatios = [reg.calculateRatio() for reg in self.regions]
        self.ratio = Util.getMeanStDev(regionRatios)
        
        regionDensity = [reg.calculateDensity() for reg in self.regions]
        self.density = Util.getMeanStDev(regionDensity)
        
        Region.setMetric(self.area, self.ratio, self.density)
        
        for reg in self.regions:
            reg.setOutliers()
        
    def addPoint(self, i, j):        
        currLabelHat = self.eqClassesHat[self.labels[i][j]]
        currLabelRegionIndex = self.eqClassesHatSingles.index(currLabelHat)
        
        self.regions[currLabelRegionIndex].addPoint(i,j)
        
        self.mask.itemset((i,j),currLabelHat)
                
    def saveRegions(self):        
        for region in self.regions:
            region.cropImg(self.mask)
                
thisCCL = CCL(imageToRead)