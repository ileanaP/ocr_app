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
        returnvalue = 'default return value'
        if operation == 'preprocessing':
            returnvalue =  '01 - got here without fuss'
            targetFilePath = os.path.join(app.config['UPLOAD_FOLDER'], self.filename.replace(".", "_preprocessing."))
            self.operator = ImagePreprocessingService(self.filePath, targetFilePath)
            returnvalue =  '02 - got here :o shocker'
        else:
            returnvalue = '03 - there is no operation ppl'
            
        return returnvalue
            