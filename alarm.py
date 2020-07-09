# -*- coding:utf-8 -*-
# /usr/bin/python3
# build up a microservice for local 
# a simple page of message box, and a interface to show it

from flask import Flask
from flask import request
from flask import render_template,url_for
# flask support

from gevent import pywsgi
from alarm_utils import ring

app = Flask(__name__)
Master = None

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
    
    ring('MicroServicev1.1','全局闹钟已经启动...')
    gserver = pywsgi.WSGIServer(("localhost",8688),app)
    gserver.serve_forever()