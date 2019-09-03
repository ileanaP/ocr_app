# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:02:52 2019

@author: ILENUCA
"""

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'try-to-guess'
    APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'app')
    UPLOAD_FOLDER = os.path.join(APP_PATH, 'static','img', 'uploads')
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024