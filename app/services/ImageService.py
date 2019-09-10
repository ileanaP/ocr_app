# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 19:43:50 2019

@author: ILENUCA
"""

import os
from app import app
from app.services.ImagePreprocessingService import ImagePreprocessingService
#from app.services.ImageSegmentationService import ImageSegmentationService

class ImageService:
    def __init__(self, filename): #s-ar putea ca filename sa fie NONE
        self.filename = filename
        self.filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        self.operator = None
        
    def apply(self, operation):
        returnvalue = '0'
        
        if operation == 'preprocessing':
            targetFilename = self.filename.replace(".", "_preprocessing.")
            targetFilePath = os.path.join(app.config['UPLOAD_FOLDER'], targetFilename)
            
            self.operator = ImagePreprocessingService(self.filePath)
            self.operator.apply(targetFilePath)
            
            if self.operator.processed:
                returnvalue =  targetFilename
        else:
            returnvalue = 'operation not yet defined'
            
        return returnvalue
            