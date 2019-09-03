# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:19:43 2019

@author: ILENUCA
"""

from flask import flash
import os
from app import app
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired
from werkzeug import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge

class UploadForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    scan = BooleanField('Scan', default="checked")
    ccl = BooleanField('Apply CCL', default="checked")
    submit = SubmitField('Upload')
    fileSize = 0
    
    def isFileExtentionAllowed(self, filename):
        ext = filename.split('.')[1].lower()
        if ext in app.config['ALLOWED_EXTENSIONS']:
            return 1
        
        return 0
    
    def setFileSize(self, file):
        file.seek(0, os.SEEK_END)
        self.fileSize = file.tell()
        file.seek(0)
    
    #include file field in form
    def tryUploadFileToServer(self):
        if self.validate_on_submit():
            try:
                file = self.file.data
            
                if not file:
                    flash('No file was uploaded. Please try again')
                    return
            except RequestEntityTooLarge: #does not work on dev env
                abort(413, 'File exceeds server capabilities')
        
            self.setFileSize(file)
            
            if self.fileSize > 3145728:
                flash("The file exceeds 3MB. Please try uploading another one")
                return
                
            self.uploadFile(file)
    
    def uploadFile(self, file):
        filename = secure_filename(file.filename)
            
        if self.isFileExtentionAllowed(filename):
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filePath)
            flash('File was successfully uploaded')
        else:
            flash('This file extention is not allowed. Please try another one')