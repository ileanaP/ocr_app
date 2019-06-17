# -*- coding: utf-8 -*-
"""
Created on Sun May 26 12:34:38 2019

@author: ILENUCA
"""

from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

from app import routes