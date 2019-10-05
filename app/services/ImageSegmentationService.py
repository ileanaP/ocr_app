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

from app import app
import sys
import os
import numpy as np
import cv2
import time
import math
import json
from app.services.Util import Util
from app.services.Line import Line
from app.services.Region import Region
from app.services.FileService import FileService

class ImageSegmentationService:
    def __init__(self, filename, filePath, kargs):
        self.filename = filename
        self.filePath = filePath
        self.eqClasses = []
        self.etiquete = []
        self.currLabel = 0;
        
        self.kargs = json.loads(kargs)

        self.processed = 0
        
    def apply(self):
        
        self.image = cv2.imread(self.filePath)        
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        self.foreground = [level < 124 for level in self.image]
        
        self.h, self.w = self.image.shape
        
        self.labels = np.zeros([self.h,self.w],dtype=np.int32)
        self.labels.fill(-1)
        
        self.mask = np.zeros([self.h,self.w],dtype=np.int32)
        self.mask.fill(-1)
        
        timeElapsed = time.time()
        
        tmp = [[self.labelPoint(i, j) for j in range(self.w) if self.foreground[i][j]]
                    for i in range(self.h)]
        
        timeElapsed = time.time() - timeElapsed
        print('# labelPoints() - ', timeElapsed)
        
        self.relabelPoints()
        self.findOutliers()
        
        Line.setBoundaries(self.lines)
        Line.setIsSymbol(self.lines, self.mask)
        
        self.show()
        
        self.processed = 1
        return
    
    def labelPoint(self, x, y):
        nbrLbls = set()
        
        for i in range(x-2, x+1):
            for j in range(y-2, y+3):
                if not (i == x and j == y):
                    if i > -1 and j > -1 and j < self.w:
                        label = self.labels[i][j]
                        nbrLbls.add(label)

        nbrLbls = {label for label in nbrLbls if label >= 0}
        if len(nbrLbls) > 0:
            self.labels[x][y] = next(iter(nbrLbls))
            
            neighborSet = set()
            for i in nbrLbls:
                neighborSet = neighborSet.union(self.eqClasses[i])
            
            neighborSet = neighborSet.union(nbrLbls)
            
            for i in neighborSet:
                self.eqClasses[i] = neighborSet
        else:
            self.labels[x][y] = self.currLabel
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

        self.removeNotEligible(self.regions)
        
        timeElapsed = time.time() - timeElapsed
        print('# relabelPoints() - ', timeElapsed)
        
    def findOutliers(self):
        self.setMetric()
        
        for reg in self.regions:            
            if reg.out["dot"]:
                self.tryFindRegionParent(reg)
        
        self.removeNotEligible(self.regions)        
        self.setMetric()        
        self.setLines()
        self.splitRegions()

        # TO DO - pentru 02, ia "Birne" ca un sg. cuvant
    
    def removeNotEligible(self, regs):
        regionsToRemove = [reg for reg in regs if not reg.isEligible()]
        
        for reg in regionsToRemove:
            self.mask[self.mask == reg.label] = -1
            self.regions.remove(reg)
            
        return [reg for reg in regs if reg not in regionsToRemove]
        
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
        
#        self.lines = [Line([reg for reg in self.regions if reg.line == i]) for i in allLines]
        self.lines = [[reg for reg in self.regions if reg.line == i] for i in allLines]
        self.lines = [self.mergeSplitRegions(line) for line in self.lines]
        self.lines = [self.removeNotEligible(line) for line in self.lines]
        self.lines = [Line(line) for line in self.lines]
        
    def mergeSplitRegions(self, line):
        line.sort(key=lambda b: b.getWest())
        
        for i in range(len(line) - 1):
            diff = line[i+1].W - line[i].E
            if diff <= 0:
                if line[i].S < line[i+1].N or line[i+1].S < line[i].N:
                    self.mask[self.mask == line[i].label] = line[i+1].label
                    line[i+1].join(line[i])
                    i = i + 1
                    
        line = [reg for reg in line if reg.N != 0]
        
        return line
        
    def join(self, reg1, reg2):
        self.mask[self.mask == reg2.label] = reg1.label
        reg1.join(reg2)
        
    def show(self):
        # TO DO - sa pun coordonatele dreptunghiurilor intr-un JSON, si sa le desenez din JS
        tempimage = cv2.imread(self.filePath)
        
        lines = []
        words = []
        regions = []
        boundaries = []
        frame = []
        
#        if self.kargs["cropped"]:
        fileNames = self.saveRegions()
        
        f = open(os.path.join(app.config["RESULTS_FOLDER"], "cropped_filenames.json"), "w")
        f.write(json.dumps(fileNames))
        f.close()
    
#        if self.kargs["lines"]:
        toggle = 0
        for line in self.lines:
            lineThickness = 2
            if line.symbol:
                lineColor = (0,0,255)
            else:
                if toggle:
                    lineColor = (192,192,192)
                    toggle = 0
                else:
                    lineColor = (230,216,173)
                    toggle = 1
            
            lines.append([line.N, line.S, line.symbol])
            cv2.line(tempimage, (0, line.N), (self.w, line.N), lineColor, lineThickness)
            cv2.line(tempimage, (0, line.S), (self.w, line.S), lineColor, lineThickness)
    
#        if self.kargs["words"]:
        for line in self.lines:
            for word in line.words:
                words.append([word.W, word.N+1, word.E, word.S+1])
                tempimage = cv2.rectangle(tempimage,(word.W,word.N+1),(word.E,word.S+1),(0,128,0),lineThickness)
            
#        if self.kargs["regions"]:
        for line in self.lines:
            for reg in line.regions:
                regions.append([reg.W, reg.N+1, reg.E, reg.S+1])
                tempimage = cv2.rectangle(tempimage,(reg.W,reg.N+1),(reg.E,reg.S+1),(34,34,178), 2)
    
#        if self.kargs["boundaries"]:
        for line in self.lines:
            tmpColor = (112,128,144)
            if line.symbol:
                tmpColor = (0,0,250)
            boundaries.append([line.W, line.N, line.E, line.S, line.symbol])
            tempimage = cv2.rectangle(tempimage,(line.W,line.N),(line.E,line.S),tmpColor,1)
        
#        if self.kargs["frame"]:
        frame.append([Line.W, Line.N, Line.E, Line.S])
        tempimage = cv2.rectangle(tempimage,(Line.W,Line.N),(Line.E,Line.S),(255,0,0),3)
        
        shape = [self.h, self.w]
        
        toJson = {
                    "shape": shape,
                    "lines": lines,
                    "words": words,
                    "regions": regions,
                    "boundaries": boundaries,
                    "frame": frame
                }
        
        self.jsonFilename = self.filename.split(".", 1)[0] + ".json"
        self.jsonPath = os.path.join(app.config["RESULTS_FOLDER"], self.jsonFilename)
        f = open(self.jsonPath, "w+")
        f.write(json.dumps(toJson))
        f.close()
        
        self.segmentedFilename = self.filename.replace(".", "_segmented.")
        
        resultsFilePath = os.path.join(app.config['RESULTS_FOLDER'], self.segmentedFilename)
        cv2.imwrite(resultsFilePath, tempimage)        
        
    def splitRegions(self):        
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
                  
                self.join(desiredRegion, reg)
#                self.mask[self.mask == reg.label] = croppedLabel
#                desiredRegion.join(reg)
                
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
        # TO DO -  daca am dat remove la regions not eligible din self.regions (gasite in lines), de ce au ramas in self.regions? xD

        FileService.cleanCroppedFolder()
        
        fileNames = [self.lines[i].regions[j].cropImg(i, j, self.mask) for i in range(len(self.lines))
                        for j in range(len(self.lines[i].regions))]
        
        return fileNames
                