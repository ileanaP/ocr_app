# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 13:38:48 2019

@author: ILENUCA
"""

import os
from app import app
import time
from werkzeug import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge

class FileService:
#    def __init__(self, file): #se da ca argument file.data al wtform

    def upload(self, file):
        try:
            if not file:
                return '1001' #no file was uploaded
            
            fileSize = self.getFileSize(file)
            if fileSize > 3145728:
                return '1002' #the file exceeds 3MB

            return self.uploadFileToServer(file)

        except RequestEntityTooLarge: #does not work on dev env
            abort(413, 'File exceeds server capabilities')
            
    def delete(self, filename):
        filename = secure_filename(filename)
        segmentedJson = self.changeFileExt(filename, "json")
        croppedJson = self.changeFileExt(filename, "cropped.json")
        
        filePath = self.getFilePath('upload', filename)
        preprocessedPath = self.getFilePath('results', filename)
        segmentedJsonPath = self.getFilePath('results', segmentedJson)
        croppedJsonPath = self.getFilePath('results', croppedJson)
        
        try:
            self.tryRemoveFile(filePath)
            self.tryRemoveFile(preprocessedPath)
            self.tryRemoveFile(segmentedJsonPath)
            self.tryRemoveFile(croppedJsonPath)
            
            self.cleanCroppedFolder()
            
            return '1007'
        except:
            return '1006'
        
    def getFileSize(self, file):
        file.seek(0, os.SEEK_END)
        fileSize = file.tell()
        file.seek(0)
        return fileSize

    #include file field in form
    def uploadFileToServer(self, file):
        filename = secure_filename(file.filename)
        fileext = self.getFileExt(filename)
        
        if self.isFileExtAllowed(fileext):
            currTimestamp = str(int(time.time()))
            filename = ".".join([currTimestamp, fileext])
            filePath = self.getFilePath('upload', filename)
            file.save(filePath)
            return filename #file was uploaded succcesfully
        else:
            return '1004' #file extention not allowed

    @staticmethod
    def isFileExtAllowed(fileext):
        return 1 if fileext in app.config['ALLOWED_EXTENSIONS'] else 0

    @staticmethod
    def tryRemoveFile(filePath):
        if os.path.exists(filePath):
            os.remove(filePath)
    
    @staticmethod
    def changeFileExt(filename, newExt):
        filename = filename.split(".", 1)[0]
        return ''.join([filename, ".", newExt])
    
    @staticmethod
    def getFileExt(filename):
        tmp = filename.split(".")
        return tmp[len(tmp)-1].lower()
    
    @staticmethod
    def getFilePath(fType, filename):
        return os.path.join(app.config[fType.upper() + '_FOLDER'], filename)
        
    @staticmethod
    def cleanCroppedFolder():
        for tmp_file in os.listdir(app.config['CROPPED_FOLDER']):
            filePathDel = os.path.join(app.config['CROPPED_FOLDER'], tmp_file)
            if os.path.isfile(filePathDel):
                os.unlink(filePathDel)