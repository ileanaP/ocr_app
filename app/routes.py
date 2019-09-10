# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:38:42 2019

@author: ILENUCA
"""

from flask import render_template, request
from flask.helpers import make_response
from app import app
from app.services.FileService import FileService
from app.services.ImageService import ImageService
from app.forms import UploadForm

@app.route('/')
@app.route('/index')
def index():
    uploadForm = UploadForm()
    return render_template('index.html', title='Home', uploadForm=uploadForm)

@app.route('/example')
def example():
    return render_template('example.html', title='Example OFC')

@app.route('/upload', methods=['GET',  'POST'])
def upload(): # TO DO - sa trimit la 404 daca se acceseaza fara sa fie POST
    uploadForm = UploadForm()
    returncode = '0'
    
    if request.method == 'POST': #this url will be POSTed only from AJAX
        if uploadForm.validate_on_submit():
            fileService = FileService()
            returncode = fileService.upload(uploadForm.file.data)
        else:
            returncode = '1005' #there was an error in submitting the form
            
    if request.method == 'GET': #to rewrite - request.args pentru GET
        filename = request.args.get('filename')
        fileService = FileService()
        returncode = fileService.delete(filename) # TO DO - sa stearga si artefacts pt fisier (_preprocessed, etc...)
    
    return returncode

@app.route('/image', methods=['GET',  'POST'])
def manipulateImage():
    returncode = '0'
    
    if request.method == 'GET':
        operation = request.args.get('operation')
        filename = request.args.get('filename')
        imageService = ImageService(filename)
        returncode = imageService.apply(operation)
        
    return returncode

""" ERROR HANDLING  """
@app.errorhandler(404)
def page_not_found(e):
    return make_response(render_template('404.html', title="404 Page Not Found"), 404)

@app.errorhandler(413) #does not work on dev env
def request_entity_too_large(e):
    return make_response(render_template('413.html', title="413 File Too Large"), 413)