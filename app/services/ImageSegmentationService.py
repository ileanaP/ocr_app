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
import scipy.misc

minimizer = lambda x: min(x)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, regions):
        self.regions = regions
        self.N, self.S = 0, 0
        self.symbol = 0
        
        self.__setCoords()
        self.__setIsSymbol()
    
    def __setCoords(self):
        self.N = min([reg.N for reg in self.regions])
        self.S = max([reg.S for reg in self.regions])
        
    def __setIsSymbol(self):
        
        symbolsNr = len([reg for reg in self.regions if reg.out["densityOver"]])
        
        print("####")
        print("symbolsNr: ", symbolsNr)
        print("allNr: ", len(self.regions))
        
        self.symbol = True if symbolsNr/len(self.regions) > 0.7 else False
        
class Region:
    def __init__(self, h, w, label):
        self.label = label
        self.imgH = h
        self.imgW = w
        
        self.h, self.w, self.area, self.ratio, self.density, self.line = 0, 0, 0, 0, 0, 0
        
#        self.splitVal = 0
#        self.isNormalRatioOver = False
#        self.isNormalRatioUnder = False
        
        self.out = {
                    "areaOver"    : False, "areaUnder"    : False, # used to determine wether a region is too big, or has more letters
                    "ratioOver"   : False, "ratioUnder"   : False, # same as above, only for small regions
                    "densityOver" : False, "densityUnder" : False, 
                    "dot"         : False
                   }
        
        self.N = h #smallest row in the list of points
        self.S = 0 #biggestt row
        self.W = w #smallest column in the list of points
        self.E = 0 #biggest column
        
    def addPoint(self, x, y):
        self.area += 1
        
        self.N = min(self.N, x)
        self.S = max(self.S, x)
        self.W = min(self.W, y)
        self.E = max(self.E, y)
    
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

        self.out['dot'] = True if (self.ratio >= 0.7 and self.ratio <= 1.3 and self.out['areaUnder']) else False

    def cropImg(self, mask):        
        self.cropped = mask[self.N:self.S+1, self.W:self.E+1]
        self.cropped = [[255 if value == self.label else 0 for value in row ] for row in self.cropped]
        self.cropped = np.asarray(self.cropped, dtype=np.int8)

        height, width = self.cropped.shape
        
        fileName = str(self.area) + '_' + str(self.label)
        
#        if self.out["areaUnder"] or self.out["areaOver"]:
#            fileName = fileName + "_AO"
#        if self.out["ratioOver"]:
#            fileName = fileName + "_RO"
#        if self.out["ratioUnder"]:
#            fileName = fileName + "_RU"
        if self.out["densityOver"]:
            fileName = fileName + "_DO"
        if self.out["densityUnder"]:
            fileName = fileName + "_DU"
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
        # vreau sa scot margins, si regions cu aria 1 - OK
        # vreau sa gasesc outliers in functie de area (standard deviation) - OK
        # dintre outlierii mici, vreau sa gasesc semne de punctuatie, puncte pe i/j, etc - OK
        # dintre outlierii mari, vreau sa gasesc daca sunt mai multe litere in ei, si sa ii sparg
        # --- in functie de ratio a elementelor care nu sunt outlieri (SD a ratio)
        # daca dintre outlierii mari sunt linii orizontale __ sau verticale | care nu sunt margini? 
        # --- scot liniile | si liniile __ devin "_ _ _ _" in textul final (SD a ratio)
        
        # sa despart literele folosindu-ma de NRO sau de width a literelor de pe aceeasi linie
        # sa leg punctul de la "!" (daca e cazul)
        # sa gasesc punct si virgula in functie de density :D
        
        self.setMetric()
        
        for reg in self.regions:
            if reg.out["dot"]:
                self.tryFindRegionParent(reg)
        
        self.regions = [reg for reg in self.regions if reg.isEligible()]
        
        self.setMetric()
#        self.setSomeRatio()
        
        # pentru a sparge regions cu mai multe litere in literele separate:
        # -- gasesc liniile, apoi gasesc mean height pe linie
        # -- gasesc mean width in functie de Mean Normal Ratio a elems care nu sunt symbols (setSomeRatio), si mean height:
        #    mW = mNR * mH
        # (ar fi bine ca din preprocesare liniile sa nu fie sloped - AR FI XD)
        # +++ sa gasesc cuvintele din fiecare linie :D <3
        self.setLines()
        
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

        tempimage = cv2.imread(imageToRead)
        
        for line in self.lines:            
            lineThickness = 2
            if line.symbol:
                lineColor = (255,0,125)
            else:
                lineColor = (125,0,255)

            cv2.line(tempimage, (0, line.N), (self.w, line.N), lineColor, lineThickness)
            cv2.line(tempimage, (0, line.S), (self.w, line.S), lineColor, lineThickness)
            
        cv2.imshow('image',tempimage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imwrite('scannedimage.jpg', tempimage)
        sys.exit()

    def getNeighborRegions(self, reg):
        
        regionMiddle = reg.N + int((reg.S - reg.N)/2)
        
        neighborLabels = self.mask[regionMiddle:regionMiddle+1,]
        
        neighbors = [r for r in self.regions if (r.label in neighborLabels and r.label != -1 )]        

        return neighbors
        
        
    def removeSlope(self):
        minN = min([reg.N for reg in self.regions])
        maxS = max([reg.S for reg in self.regions])
        minW = min([reg.W for reg in self.regions])
        maxE = max([reg.E for reg in self.regions])
        
    def tryFindRegionParent(self, reg):
        if reg.out["dot"]:
            areaH = reg.h * 4
            
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
        
                
#    def setSomeRatio(self):
#        regionsTemp = [reg.ratio for reg in self.regions if reg.out["densityOver"] is not True]
#
#        tmp = self.getMeanStDev(regionsTemp)
#        
#        for reg in self.regions:
#            reg.isNormalRatioOver = True if reg.ratio > tmp['m'] + tmp['sd'] else False
#            reg.isNormalRatioUnder = True if reg.ratio < tmp['m'] - tmp['sd'] else False
#            if reg.ratio > tmp['m'] + tmp['sd'] and reg.out["areaOver"]:
#                meanW = tmp["m"] * reg.h
#                if reg.area == 962:
#                    print("meanW: ", meanW)
#                splitValue = int(round(meanW))
#                if reg.area == 375:
#                    print("splitValue: ", splitValue)
#                    print("reg w: ", reg.w)
#                reg.splitVal =int(round(reg.w/splitValue))
#                if reg.area == 375:
#                    print("reg splitVal: ", reg.splitVal)
#                    sys.exit()
                
    def setMetric(self):
        regionAreas = [reg.area for reg in self.regions]
        self.area = self.getMeanStDev(regionAreas) # get area mean (M) and area standard deviation (SD)
        
        regionRatios = [reg.calculateRatio() for reg in self.regions]
        self.ratio = self.getMeanStDev(regionRatios)
        
        regionDensity = [reg.calculateDensity() for reg in self.regions]
        self.density = self.getMeanStDev(regionDensity)
        
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
        
    def getMeanStDev(self, elems):
        mean = sum(elems) / len(elems)
        stDev = statistics.pstdev(elems) # standard deviation
        
        return { 'm': mean, 'sd': stDev }
        
    def addPoint(self, i, j):        
        currLabelHat = self.eqClassesHat[self.labels[i][j]]
        currLabelRegionIndex = self.eqClassesHatSingles.index(currLabelHat)
        
        self.regions[currLabelRegionIndex].addPoint(i,j)
        
        self.mask.itemset((i,j),currLabelHat)
                
    def saveRegions(self):        
        for region in self.regions:
            region.cropImg(self.mask)
                
thisCCL = CCL(imageToRead)