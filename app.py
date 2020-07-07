# -*- coding:utf-8 -*-
# /usr/bin/python3
# build up a microservice for local 
# a simple page of message box, and a interface to show it

from flask import Flask
from flask import request
from flask import render_template,url_for
# flask support

from utils import ring

__version__ = 1.0
app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    '''do nothing here'''
    
    if request.method == 'GET':
        return 'local service alarm{}'.format(__version__)

@app.route("/alarm",methods=['POST'])
def alarm():

    if request.method == 'POST':
        if request.json is None:
            return "interface error : missing parameters"
        try:
            title = request.json['title']
            content = request.json['content']

            ring(title,content)
            return f"call successfully"
        except KeyError as e:
            return f"interface error : missing parameter:{e}"


if __name__ == "__main__":
    
    app.run(host="localhost",port=8688,debug=True)