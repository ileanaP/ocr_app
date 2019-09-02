# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, flash, redirect, url_for, request
import os
#from werkzeug import secure_filename
from app import app
from app.forms import UploadForm
#from scanner import ImageScanner
import scripts.scanner

def getAllowedExt(filename):
    if '.' in filename:
        ext = filename.split('.')[1].lower()
        if ext in app.config['ALLOWED_EXTENSIONS']:
            return ext
        else:
            return ''
    else:
        return ''

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/example')
def example():
    return render_template('exaple.html', title='Home')

@app.route('/upload', methods=['GET',  'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file was uploaded. Please try again')
                return redirect(url_for(upload))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file was uploaded. Please try again')
            else:
                ext = getAllowedExt(file.filename)
                if file and ext != '':
                    fileWay = os.path.join(app.config['UPLOAD_FOLDER'], 'reciept.' + ext)
                    file.save(fileWay)
                    flash('File was successfully uploaded')
                else:
                    flash('This file extention is not allowed. Please try another one')
#            
    return render_template('upload.html', title="Upload Form", form=form)