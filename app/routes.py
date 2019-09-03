# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, flash, request
from flask.helpers import make_response
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
    return make_response(render_template('404.html', title="404 Page Not Found"), 404)

@app.errorhandler(413)
def request_entity_too_large(e):
    return make_response(render_template('413.html', title="413 File Too Large"), 413)