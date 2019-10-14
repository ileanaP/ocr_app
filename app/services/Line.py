# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 15:36:10 2019

@author: ILENUCA
"""

from app import app
from app.services.Word import Word
from app.services.Util import Util

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
            
#    def mergeSplitRegions(self, mask):
#        self.sortWestEast()
#        
#        for i in range(len(self.regions) - 1):
#            diff = self.regions[i+1].W - self.regions[i].E
#            if diff <= 0:
#                if self.regions[i].S < self.regions[i+1].N or self.regions[i+1].S < self.regions[i].N:
#                    mask[mask == self.regions[i].label] = self.regions[i+1].label
#                    self.regions[i+1].join(self.regions[i])
#                    i = i + 1
#        
#        self.regions = [reg for reg in self.regions if reg.N != 0]
#
#        return 1


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
    def setIsSymbol(lines, mask):
#        tmp = [line.mergeSplitRegions(mask) for line in lines]

        for line in lines:
            line.findWords()
            line.setWordBoundaries()
        
        #try to find outliers by number of regions in line
        nrRegs = [len(line.regions) for line in lines]
        nrRegs = Util.getMeanStDev(nrRegs)
        
        outlierLines = [line for line in lines if (len(line.regions) > nrRegs['m']+nrRegs['sd']) and len(line.words) == 1]
        
        for line in outlierLines:
            line.symbol = True