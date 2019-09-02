# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import UploadForm

def isFileExtentionAllowed(filename):
    ext = filename.split('.')[1].lower()
    if ext in app.config['ALLOWED_EXTENSIONS']:
        return 1
    
    return 0

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/example')
def example():
    return render_template('example.html', title='Example OFC')

@app.route('/upload', methods=['GET',  'POST'])
def upload():
    form = UploadForm()
    if request.method == 'POST':
#        if 'file' not in request.files:
#            flash('No file was uploaded. Please try again - from routes')
#        else:
        form.tryUploadFileToServer()
            
    return render_template('upload.html', title="Upload Form", form=form)