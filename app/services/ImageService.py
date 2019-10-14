# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 19:43:50 2019

@author: ILENUCA
"""

import os
from app import app
from app.services.ImagePreprocessingService import ImagePreprocessingService
from app.services.ImageSegmentationService import ImageSegmentationService
from app.services.FileService import FileService as fs
import json
#from app.services.ImageSegmentationService import ImageSegmentationService

class ImageService:
    def __init__(self, filename, kargs): #s-ar putea ca filename sa fie NONE
        self.filename = filename
        self.kargs = kargs
        self.filePath = fs.getFilePath('upload', filename)
        self.operator = None

        self.targetFilePath = fs.getFilePath('results', self.filename)
        
    def apply(self, operation):
        returnvalue = '0'
        
        if operation == 'preprocessing':
            
            self.operator = ImagePreprocessingService(self.filePath)
            self.operator.apply(self.targetFilePath)
            
            if self.operator.processed:
                returnvalue = self.filename
                
        elif operation == 'segmentation':
            
            filenames = [fs.changeFileExt(self.filename, "json"), fs.changeFileExt(self.filename, "cropped.json")]
            
            segmentedJsonPath = fs.getFilePath('results', filenames[0])
            croppedJsonPath = fs.getFilePath('results', filenames[1])
            
            self.operator = ImageSegmentationService(self.targetFilePath, croppedJsonPath, segmentedJsonPath, self.kargs) # sa ma folosesc de filePath            
            self.operator.apply()
            
            if self.operator.processed:
                returnvalue = json.dumps(filenames)
                
        else:
            returnvalue = 'operation not yet defined'
            
        return returnvalue
            