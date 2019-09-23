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
import sys
import time
import statistics
import math
import scipy.misc

minimizer = lambda x: min(x)

def sortByPosition(reg1, reg2):
    returnValue = 0
    
    if reg1.W < reg2.W:
        returnValue = -1
    if reg1.W > reg2.W:
        returnValue =1 
    
    return returnValue

class Util:
    @staticmethod
    def getMeanStDev(elems):
        mean = sum(elems) / len(elems)
        stDev = statistics.pstdev(elems) # standard deviation
        
        return { 'm': mean, 'sd': stDev }

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

class Line:
    N, S, W, E = 0, 0, 0, 0
    def __init__(self, regions):
        self.regions = regions
        self.N, self.S, self.W, self.E = 0, 0, 0, 0
        self.symbol = 0
        self.outlier = False
        
        self.__setCoords()
        self.__setIsSymbol()
    
    def __setCoords(self):
        self.N = min([reg.N for reg in self.regions])
        self.S = max([reg.S for reg in self.regions])
        
    def __setIsSymbol(self):
        
        symbolsNr = len([reg for reg in self.regions if reg.out["densityOver"]])        
        self.symbol = True if symbolsNr/len(self.regions) > 0.7 else False
        
    def sortWestEast(self): #sort regions from left to right
        self.regions.sort(key=lambda b: b.getWest())
        
    def findWords(self):
        # TO DO - ar fi mai ok sa caut pe verticala dupa line height 
        self.sortWestEast()
        
        word = Word()
        self.words = []
        
        for i in range(len(self.regions)):
            word.add(self.regions[i])
            if i < len(self.regions)-1 and self.regions[i+1].isNear(self.regions[i]):
                continue
            else:
                self.words.append(word)
                word = Word()
             
        if len(word.regions) > 0:
            self.words.append(word)
            
    def setWordBoundaries(self):
        tmp = [word.setBoundaries() for word in self.words]
            
    def mergeSplitRegions(self):
        self.sortWestEast()
        
        for i in range(len(self.regions) - 1):
            diff = self.regions[i+1].W - self.regions[i].E
            if diff <= 0:
                if self.regions[i].S < self.regions[i+1].N or self.regions[i+1].S < self.regions[i].N:
                    self.regions[i+1].join(self.regions[i])
                    i = i + 1
        
        self.regions = [reg for reg in self.regions if reg.N != 0]

        return 1


    @classmethod
    def setBoundaries(cls, lines):
        for line in lines:  
            line.N = min([x.N for x in line.regions])
            line.S = max([x.S for x in line.regions])
            line.W = min([x.W for x in line.regions])
            line.E = max([x.E for x in line.regions])
            
        cls.N = min([line.N for line in lines])
        cls.S = max([line.S for line in lines])
        cls.W = min([line.W for line in lines])
        cls.E = max([line.E for line in lines])
        
    @staticmethod
    def setIsSymbol(lines):
        tmp = [line.mergeSplitRegions() for line in lines]

        for line in lines:
            line.findWords()
            line.setWordBoundaries()
        
        #try to find outliers by number of regions in line
        nrRegs = [len(line.regions) for line in lines]
        nrRegs = Util.getMeanStDev(nrRegs)
        
        outlierLines = [line for line in lines if (len(line.regions) > nrRegs['m']+nrRegs['sd']) and len(line.words) == 1]
        
        for line in outlierLines:
            line.symbol = True
        
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
        
        return returnValue
        
    def calculateRatio(self):
        self.h = self.S - self.N + 1
        self.w = self.E - self.W + 1

        self.ratio = float(self.w)/float(self.h)
        
        return self.ratio
    
    def calculateDensity(self):
        if self.area != 0:
            totalArea = (self.S - self.N) * (self.E - self.W)
            
            if totalArea == 0:
                print("N: ", self.N)
                print("S: ", self.S)
                print("W: ", self.W)
                print("E: ", self.E)
                sys.exit()
                
            self.density = self.area/totalArea
            
        return self.density
    
    def join(self, reg):
        self.area = self.area + reg.area
        
        self.N = min(self.N, reg.N)
        self.S = max(self.S, reg.S)
        self.W = min(self.W, reg.W)
        self.E = max(self.E, reg.E)
        
#        print("_____")
#        self.printCoords()
#        print("=====")
        
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
                                                                 
#        if self.N == 67 and self.S == 72:
#            print("==")
#            print("area under: ", self.out["areaUnder"])
#            print("density over: ", self.out["densityOver"])
#            print("ratio: ", self.ratio)
#            sys.exit()
            
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
            

    def cropImg(self, mask):        
        self.cropped = mask[self.N:self.S+1, self.W:self.E+1]
        self.cropped = [[255 if value == self.label else 0 for value in row ] for row in self.cropped]
        self.cropped = np.asarray(self.cropped, dtype=np.int8)

        height, width = self.cropped.shape
        
        fileName = str(self.area) + '_' + str(self.label)
                
#        fileName = fileName + "_N" + str(self.N) + "S" + str(self.S) + "W" + str(self.W) + "E" + str(self.E) + ".png"
        fileName = fileName + ".png"
        
        scipy.misc.imsave('cropped/' + fileName, self.cropped)

class CCL:
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
        print('Label Points Better - ', timeElapsed)
        
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

        self.regions = [reg for reg in self.regions if reg.isEligible()]
        
        timeElapsed = time.time() - timeElapsed
        print('Relabel Points - ', timeElapsed)
        
    def findOutliers(self):
        self.setMetric()
        
        for reg in self.regions:            
            if reg.out["dot"]:
                self.tryFindRegionParent(reg)
        
        self.regions = [reg for reg in self.regions if reg.isEligible()]
        
        self.setMetric()
        
        self.setLines()
        self.otherThanSetLines()
        self.show()
        # TO DO - pentru 02, ia "Birne" ca un sg. cuvant
        
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
#                print("__", len(line.words),"__")
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
        
        print("~~~~")
        print("area Mean: ", self.area['m'])
        print("area SD: ", self.area['sd'])
        print("ratio Mean: ", self.ratio['m'])
        print("ratio SD: ", self.ratio['sd'])
        print("density Mean: ", self.density['m'])
        print("density SD: ", self.density['sd'])
        print("~~~~")
        
    def addPoint(self, i, j):        
        currLabelHat = self.eqClassesHat[self.labels[i][j]]
        currLabelRegionIndex = self.eqClassesHatSingles.index(currLabelHat)
        
        self.regions[currLabelRegionIndex].addPoint(i,j)
        
        self.mask.itemset((i,j),currLabelHat)
                
    def saveRegions(self):        
        for region in self.regions:
            region.cropImg(self.mask)
                
thisCCL = CCL(imageToRead)