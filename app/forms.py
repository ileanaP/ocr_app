# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:19:43 2019

@author: ILENUCA
"""

from app import app
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    submit = SubmitField('Upload')