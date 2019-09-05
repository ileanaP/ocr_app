# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, request
from flask.helpers import make_response
from app.services.UploadFileService import UploadFileService
from app import app
from app.forms import UploadForm

@app.route('/')
@app.route('/index')
def index():
    form = UploadForm()
    return render_template('index.html', title='Home', form=form)

@app.route('/example')
def example():
    return render_template('example.html', title='Example OFC')

@app.route('/upload', methods=['GET',  'POST'])
def upload(): # TO DO - sa trimit la 404 daca se acceseaza fara sa fie POST
    form = UploadForm()
    returncode = 0
    if request.method == 'POST': #this url will be POSTed only from AJAX
        if form.validate_on_submit():
            uploader = UploadFileService()
            returncode = uploader.upload(form.file.data)
        else:
            returncode = '1005' #there was an error in submitting the form
    return returncode
#    return render_template('upload.html', title="Upload Form", form=form)

""" ERROR HANDLING  """
@app.errorhandler(404)
def page_not_found(e):
    return make_response(render_template('404.html', title="404 Page Not Found"), 404)

@app.errorhandler(413) #does not work on dev env
def request_entity_too_large(e):
    return make_response(render_template('413.html', title="413 File Too Large"), 413)