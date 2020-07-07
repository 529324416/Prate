# -*- coding:utf-8 -*-
# /usr/bin/python3
# a script provide a messagebox based on pyqt5 & webkit
# time: 2020.07.07

__author__ = "biscuit"

from PyQt5 import QtMultimedia
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# pyqt support

import sys
import time
import threading
# std support

from _entry import *
# personal support

class _custom_window_base(QWidget):
    '''a window type based on qwidget which has fully transparent 
    window body but you can see the widgets on it'''

    def __init__(self,initialized=False):
        '''set window's base attributes, you can set initialized = False to do this'''

        super(_custom_window_base,self).__init__(None)
        if initialized:self.__build()

    def __build(self):
        '''initialize base components on window'''

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName(FATHER_)
        self.setStyleSheet(transbk_father)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

class _browser(_custom_window_base):
    '''put a webengineview on the centre position, and all the information 
    will show on the web view page, just like a browser, and this browser is based on
    google webkit'''

    def __init__(self):
        '''use a boxlayout to hold it'''

        super(_browser,self).__init__(True)
        self.__install()
    
    def __install(self):
        '''create a page to show information on it'''

        self._ = QHBoxLayout(self)
        self.face = QWebEngineView()
        self._.addWidget(self.face)

class _single_label(_custom_window_base):
    '''put a qlabel on this window to show some information'''

    def __init__(self):

        super(_single_label,self).__init__(True)
        self.__install()

    def __install(self):
        '''create a qlabel to show information on it'''

        self._ = QHBoxLayout(self)
        self.face = QLabel()
        self._.addWidget(self.face)
        self.setLayout(self._)
        self.face.setObjectName(FACE_)
        self.face.setStyleSheet(face_attr)
        
class AlarmTimer(QThread):

    transparent_clt = pyqtSignal(float)
    ring = pyqtSignal()

    def __init__(self,face,stay=15):

        super(AlarmTimer,self).__init__()
        self.box = face
        self.stay_seconds = stay
        self.complete = False

    def run(self):

        
        for i in range(1,21):
            self.transparent_clt.emit(0.05 * i)
            time.sleep(0.01)
        self.complete = True
        sound = QtMultimedia.QSound(self.box.sound_path)
        self.ring.emit()
        for i in range(self.stay_seconds):time.sleep(1)
        self.box.ctl_end.start()

class AlarmTimerDone(QThread):

    transparent_clt = pyqtSignal(float)

    def __init__(self,face):

        super(AlarmTimerDone,self).__init__()
        self.box = face

    def run(self):

        for i in range(21,0,-1):
            self.transparent_clt.emit(0.05 * i)
            time.sleep(0.02)
        self.box.hide()
        QCoreApplication.instance().quit
        

class AlarmWindow(_single_label):
    '''a window based on webkit'''

    def __init__(self,sound_path,title,content):

        super(AlarmWindow,self).__init__()
        self.sound_path = sound_path
        self.make_up(title,content)
        self.build()
        

    def make_up(self,title,content):
        '''build something on face'''

        self.layout_ = QVBoxLayout()
        font_id = QFontDatabase.addApplicationFont("./resource/hanyizhuzi.ttf")
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font = QFont(font_name,18)
        self.header = QLabel()
        self.header.setFont(self.font)
        self.header.setAlignment(Qt.AlignLeft)
        self.header.setFixedHeight(30)
        

        self.header.setStyleSheet(r"QLabel{color:rgb(80,80,80)}")
        self.body = QLabel()
        self.body.setStyleSheet(r"QLabel{color:rgb(96,96,96)}")
        self.font_content = QFont(font_name,15)
        self.body.setFont(self.font_content)
        self.body.setAlignment(Qt.AlignLeft)
        self.layout_.addWidget(self.header)
        self.layout_.addWidget(self.body)
        self.face.setLayout(self.layout_)
        self.header.setText(title)
        self.body.setText(content)
    
    def build(self):
        '''initialize base components'''

        self.ctl = AlarmTimer(self,stay=10)
        self.ctl.transparent_clt.connect(self.set_tranparency)
        self.ctl.ring.connect(self.play_sound)
        self.ctl_end = AlarmTimerDone(self)
        self.ctl_end.transparent_clt.connect(self.set_tranparency)
        self.player = QtMultimedia.QMediaPlayer()
        self.sound = QtMultimedia.QMediaContent(QUrl(self.sound_path))
        self.resize(300,350)
        self.show()

    def mousePressEvent(self,evt):
        '''when use clicked window, then close it'''

        if self.ctl.complete:
            self.ctl.quit()
            self.ctl_end.start()

    def play_sound(self):

        self.player.setMedia(self.sound)
        self.player.play()

    def set_tranparency(self,transparency):
        '''set window transparency of current window
        @transparency: a float value between 0 and 1'''

        self.setWindowOpacity(transparency)

def __ring(title,content):

    app = QApplication(sys.argv)
    window = AlarmWindow("./resource/8736.wav",title,content)
    window.ctl.start()
    sys.exit(app.exec_())

def ring(title,content):

    t = threading.Thread(target=__ring,args=(title,content))
    t.start()