# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:19:43 2019

@author: ILENUCA
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    scan = BooleanField('Scan', default="checked")
    ccl = BooleanField('Apply CCL', default="checked")
    submit = SubmitField('Upload')
    
    #include file field in form