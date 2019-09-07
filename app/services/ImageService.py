# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 19:43:50 2019

@author: ILENUCA
"""

import os
from app import app
from app.services.ImagePreprocessService import ImagePreprocessService
from app.services.ImageSegmentationService import ImageSegmentationService

class ImageService:
    def __init__(self, filename): #s-ar putea ca filename sa fie NONE
        self.filename = filename
        self.filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)