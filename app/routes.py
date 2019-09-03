# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, flash, redirect, url_for, request
import os
from app import app
from app.forms import UploadForm

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
        form.tryUploadFileToServer()
    return render_template('upload.html', title="Upload Form", form=form)

""" ERROR HANDLING  """
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="404 Not Found")