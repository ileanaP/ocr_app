# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 13:38:48 2019

@author: ILENUCA
"""

import os
from app import app
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
        filePath = self.getFilePath(filename)
        
        try:
            os.remove(filePath)
            return '1007'
        except:
            return '1006'

    def getFilePath(self, filename):
        return os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
    def isFileExtentionAllowed(self, filename): #ar putea fi imbunatatit
            ext = filename.split('.')[1].lower()
            if ext in app.config['ALLOWED_EXTENSIONS']:
                return 1
            return 0
        
    def getFileSize(self, file):
        file.seek(0, os.SEEK_END)
        fileSize = file.tell()
        file.seek(0)
        return fileSize

    #include file field in form
    def uploadFileToServer(self, file):
        filename = secure_filename(file.filename)
        
        if self.isFileExtentionAllowed(filename):
            filePath = self.getFilePath(filename)
            file.save(filePath) #TO DO - sa adauge un 01 la finalul numelui fisierului daca numele exista deja
            return filename #file was uploaded succcesfully
        else:
            return '1004' #file extention not allowed