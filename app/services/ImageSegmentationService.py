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

imageToRead = "ccl_image_02.jpg"

import numpy as np
import cv2
import sys
import time
import statistics
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
    
#    @staticmethod
#    def sortByPosition(reg1, reg2):
#        returnValue = 0
#        
#        if reg1.W < reg2.W:
#            returnValue = -1
#        if reg1.W > reg2.W:
#            returnValue =1 
#        
#        return returnValue

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, regions):
        self.regions = regions
        self.N, self.S = 0, 0
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
        
    @staticmethod
    def setIsSymbol(lines):
        
        tempimage = cv2.imread(imageToRead)
        
        diffBetween = []
        
        for line in lines:
#### showing lines and regions and stuff ##
#            
#            
#            minN = min([x.N for x in line.regions])
#            maxS = max([x.S for x in line.regions])
#            minW = min([x.W for x in line.regions])
#            maxE = max([x.E for x in line.regions])
#            
#            for reg in line.regions:
#                tempimage = cv2.rectangle(tempimage,(reg.W,reg.N),(reg.E,reg.S),(255,0,255),1)
#                
#            tempimage = cv2.rectangle(tempimage,(minW,minN),(maxE,maxS),(0,0,255),2)
#            
#        cv2.imshow('image',tempimage)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()
#
#        cv2.imwrite('scannedimage.jpg', tempimage)
#        sys.exit()
####
        # TO DO pt MAINE - sa gasesc cuvinte in functie de SD a distantei dintre litere <3 ++ randuri de simboluri ^_^

        for line in lines:
            line.regions.sort(key=lambda b: b.getWest()) #sort regions from left to right
            diffBetween = []
            
            for i in range(len(line.regions) - 1):
                
                diff = line.regions[i+1].W - line.regions[i].E
                print("_______++++++_______++++++++")
                if diff < 0:
                    print("___")
                    print("N: ", line.regions[i].N)
                    print("S: ", line.regions[i].S)
                    print("W: ", line.regions[i].W)
                    print("E: ", line.regions[i].E)
                    print("___")
                    print("N: ", line.regions[i+1].N)
                    print("S: ", line.regions[i+1].S)
                    print("W: ", line.regions[i+1].W)
                    print("E: ", line.regions[i+1].E)
                    
                    sys.exit()
                    
                diffBetween.append(diff)
            
            print("==__==__==")
            print(diffBetween)
#            sys.exit()
            
        lines.sort(key=lambda b: b.W)
        
        lineElemCount = [len(line.regions) for line in lines if len(line.regions) > 2]
        print(lineElemCount)
        
        lineElemCountMSD = Util.getMeanStDev(lineElemCount)
        print(lineElemCountMSD)
        outlierLines = [line for line in lines if len(line.regions) > lineElemCountMSD['m'] + lineElemCountMSD['sd']]
        
        for line in outlierLines:
            line.symbol = True
        
class Region:
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
        
    def wipe(self):
        self.area = 0
        
        self.N, self.S, self.W, self.E = 0, 0, 0, 0
        
    def setOutliers(self, area, ratio, density):        
        self.calculateRatio()
        
        self.out['areaOver']     = True if self.area    > area['m']    + area['sd']    else False
        self.out['areaUnder']    = True if self.area    < area['m']    - area['sd']    else False
        self.out['ratioOver']    = True if self.ratio   > ratio['m']   + ratio['sd']   else False
        self.out['ratioUnder']   = True if self.ratio   < ratio['m']   - ratio['sd']   else False
        self.out['densityOver']  = True if self.density > density['m'] + density['sd'] else False
        self.out['densityUnder'] = True if self.density < density['m'] - density['sd'] else False
            
        self.out['dot'] = False
        
        if self.ratio >= 0.6 and self.ratio <= 1.4:
            if self.out['areaUnder'] or self.out['densityOver']: # TO DO - am adaugat aici "densityOver"
                self.out['dot'] = True                           # pentru a rezolva ca in _02 nu se grupau ":" pentru ca unul din ei
                                                                 # nu era dot - modifica asta ceva la rezultatele de pana acum?
                                                                 # (de ex. pt ",")
        
    def getSplitRegions(self, meanWidth, mask, currLabel):
        
        regions = []
        
        if self.out["ratioOver"] and not (self.out["areaUnder"] or self.out["densityOver"]):
            nrSplit = int(self.w/meanWidth)
            nrSplit = int((self.w - nrSplit*2)/meanWidth)
            
            if nrSplit > 1:
                regions, currLabel = self.split(nrSplit, mask, currLabel)
                
        return regions, currLabel
        
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
        
        if self.out["areaUnder"] or self.out["areaOver"]:
            fileName = fileName + "_AO"
#        if self.out["ratioOver"]:
#            fileName = fileName + "_RO"
#        if self.out["ratioUnder"]:
#            fileName = fileName + "_RU"
#        if self.out["densityOver"]:
#            fileName = fileName + "_DO"
#        if self.out["densityUnder"]:
#            fileName = fileName + "_DU"
        if self.out["dot"]:
            fileName = fileName + "_DOT"
#        if self.isMargin():
#            fileName = fileName + "_M"
                
        fileName = fileName + "_N" + str(self.N) + "S" + str(self.S) + "W" + str(self.W) + "E" + str(self.E) + ".png"
        fileName = fileName + ".png"
        
#        if self.area == 235:
#            print("N: ", self.N)
#            print("S: ", self.S)
#            print("W: ", self.W)
#            print("E: ", self.E)
#            sys.exit()
        
        if self.area == 501:
            print("area 51 RATIO: ", self.ratio)
            print("area 51 WIDTH: ", self.w)
            print("area 51 HEIGHT: ", self.h)
        
        scipy.misc.imsave('cropped/' + fileName, self.cropped)
#        print(str(self.area) + '_' + str(self.label) + '.png', end=', ')

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
        self.showLines()
        
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
        
    def showLines(self):
        tempimage = cv2.imread(imageToRead)
        
        for line in self.lines:
            lineThickness = 1
            if line.symbol:
                lineColor = (255,255,0)
            else:
                lineColor = (125,125,125)

            cv2.line(tempimage, (0, line.N), (self.w, line.N), lineColor, lineThickness)
            cv2.line(tempimage, (0, line.S), (self.w, line.S), lineColor, lineThickness)

        cv2.imshow('image',tempimage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imwrite('scannedimage.jpg', tempimage)
#       tempimage = cv2.rectangle(tempimage,(reg.W,reg.N),(reg.E,reg.S),(0,0,255),2)
        
    def otherThanSetLines(self):        
        #get ratio of elemes not symbols and not area under or over
        normalRatios = [reg.ratio for reg in self.regions 
                            if not (reg.out["densityOver"] or reg.out["areaOver"] or reg.out["areaUnder"])]
        normalRatio = Util.getMeanStDev(normalRatios)
        
        for line in self.lines:
            widths = [reg.w for reg in line.regions]
            width = Util.getMeanStDev(widths)
            
            meanWidth = normalRatio['m'] * width['m']
            
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
                reg.wipe()

                desiredRegion.setOutliers(self.area, self.ratio, self.density)
                reg.setOutliers(self.area, self.ratio, self.density)
                
    def setMetric(self):
        regionAreas = [reg.area for reg in self.regions]
        self.area = Util.getMeanStDev(regionAreas) # get area mean (M) and area standard deviation (SD)
        
        regionRatios = [reg.calculateRatio() for reg in self.regions]
        self.ratio = Util.getMeanStDev(regionRatios)
        
        regionDensity = [reg.calculateDensity() for reg in self.regions]
        self.density = Util.getMeanStDev(regionDensity)
        
        for reg in self.regions:
            reg.setOutliers(self.area, self.ratio, self.density)
        
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