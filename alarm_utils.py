# -*- coding:utf-8 -*-
# /usr/bin/python3
# provide some basic utils for alarm
# you can set the window configs of each window level
# time: 2020.07.09

__author__ = 'biscuit'
__version__ = '1.1'

from PyQt5 import QtMultimedia
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# third support

import sys
import time
import json
import multiprocessing
# std support

from alarm_con import *

class _move_component(QLabel):
    '''make a window can be moved'''

    def __init__(self,parent):
        '''initialize base attributes'''

        super(_move_component,self).__init__(parent)
        self.__can_move = False
        self.__unlock = True
        self.__father = parent
        self._evt_handler = self.__mouse_move
        self._pos = self.pos
        if self.__father:
            self._evt_handler = self.__mouse_move_father
            self._pos = self._global_pos

    def _global_pos(self):
        '''get father's screen pos'''

        return self.mapToGlobal(self.pos())

    def mousePressEvent(self,evt:QMouseEvent):
        '''set __can_move as True when mouse clicked'''

        self.__can_move = True
        self.__distance = evt.globalPos() - self._pos()

    def mouseMoveEvent(self,evt:QMouseEvent):
        '''when clicked, window should can be moved with mouse'''

        if self.__unlock:
            self._evt_handler(evt)

    def mouseReleaseEvent(self,evt:QMouseEvent):
        '''release __can_move'''

        self.__can_move = False

    def __mouse_move(self,evt):
        '''when clicked this window, then it can be drag to other position'''

        if self.__can_move:
            self.move(evt.globalPos()-self.__distance)

    def __mouse_move_father(self,evt):
        '''this function required that the _move_component must be the son window
        instead of father window'''

        if self.__can_move:
            self.__father.move(evt.globalPos() - self.__distance)

    def lock(self):
        '''lock window and make it unmovable'''

        self.__unlock = False

    def unlock(self):
        '''cancel the lock status'''

        self.__unlock = True

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
        self.setObjectName(BASIC_WINDOW_NAME)
        self.setStyleSheet(BASIC_WINDOW_BACKCOLOR)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

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
            time.sleep(0.03)
        self.complete = True;self.ring.emit()
        time.sleep(self.stay_seconds)
        self.box.fish.start()

class AlarmTimerDone(QThread):

    transparent_clt = pyqtSignal(float)
    stop = pyqtSignal()

    def __init__(self,face):

        super(AlarmTimerDone,self).__init__()
        self.box = face

    def run(self):

        for i in range(21,0,-1):
            self.transparent_clt.emit(0.05 * i)
            time.sleep(0.02)
        self.box.hide()
        self.stop.emit()

class AlarmMessageBox(_custom_window_base):
    '''put a qlabel on this window to show some information'''

    def __init__(self,configs):

        super(AlarmMessageBox,self).__init__(True)
        self.face = QLabel()
        self.face.setObjectName(FACE_WINDOW_NAME)
        self.face.setStyleSheet(configs[CFG_KEY_FACE_ATTRS])
        self.box = QHBoxLayout(self)
        self.box.addWidget(self.face)
        self.setLayout(self.box)
        self.resize(configs[CFG_WINDOW_WIDTH],configs[CFG_WINDOW_HEIGHT])
        self.move(*get_position(configs[CFG_WINDOW_POSITION],self.width(),self.height()))
        self.build_clt(configs)
        self.set_transparency(0)
        self.show()

    def make_up(self,configs,title,content):
        '''set basic information of the current window, and set some configs about
        title or content'''

        fn = self.load_font(configs[CFG_FONT_PATH])
        font_title = QFont(fn,configs[CFG_TITLE_SIZE])
        font_content = QFont(fn,configs[CFG_CONTENT_SIZE])

        self.title_box = QLabel(self.omit(title,configs[CFG_TITLE_SIZE]))
        self.title_box.setFont(font_title)
        self.title_box.setFixedHeight(compute_font_pixel(configs[CFG_TITLE_SIZE]))
        self.title_box.setAlignment(Qt.AlignLeft)
        self.title_box.setStyleSheet(r"QLabel{color:rgb(96,96,96);}")

        self.content_box = QLabel(content)
        self.content_box.setWordWrap(True)
        self.content_box.setAlignment(Qt.AlignLeft)
        self.content_box.setFont(font_content)
        self.content_box.setStyleSheet(r"QLabel{color:rgb(128,128,128);}")

        self.facebox = QVBoxLayout(self.face)
        self.facebox.addWidget(self.title_box)
        self.facebox.addWidget(self.content_box)
        self.face.setLayout(self.facebox)

    def build_clt(self,configs):

        self.alert = AlarmTimer(self,configs[CFG_KEY_STAY])
        self.alert.transparent_clt.connect(self.set_transparency)
        self.alert.ring.connect(self.play_sound)

        self.fish = AlarmTimerDone(self)
        self.fish.stop.connect(self.close)
        self.fish.transparent_clt.connect(self.set_transparency)
    
    def mouseDoubleClickEvent(self,evt):

        if self.alert.complete:
            self.alert.quit()
            self.fish.start()
        
    def play_sound(self):

        pass

    def set_transparency(self,transparency):

        self.setWindowOpacity(transparency)

    def load_font(self,filepath):
        '''load font and return font_name'''

        font_id = QFontDatabase.addApplicationFont(filepath)
        font_name = QFontDatabase.applicationFontFamilies(font_id)[0]
        return font_name

    def omit(self,title,size):
        '''if title has exceed the maxsize, then the exceeded part 
        will be omit'''

        total = compute_char_number(size,self.width())
        return title if total > len(title) else title[:total - 2] + ".."



compute_font_pixel = lambda font_size:int((font_size/30) * 72)
compute_char_number = lambda size,length:round(length/compute_font_pixel(size))

class AlarmPosition:
    '''mark the position of desktop'''

    BOTTOM_RIGHT = 'bottom_right'
    CENTER = 'center'

def get_position(pos,width,height):
    '''compute the position where would alarm box pop out'''

    topsize = QApplication.desktop().size()
    topw,toph = topsize.width(),topsize.height()
    if pos == AlarmPosition.BOTTOM_RIGHT:
        return topw - width,toph - height
    elif pos == AlarmPosition.CENTER:
        return int((topw - width)/2),int((toph - height)/2)

def _ring(title,content,filepath="./configs.json"):

    app = QApplication(sys.argv)
    with open("./configs.json","r",encoding='utf-8') as f:
        configs = json.load(f)
    window = AlarmMessageBox(configs)
    window.make_up(configs,title,content)
    window.alert.start()
    sys.exit(app.exec_())


def ring(title,content):

    process = multiprocessing.Process(target=_ring,args=(title,content))
    process.start()

class Ring(QThread):

    def __init__(self,filepath,title,content):

        with open("./configs.json","r",encoding='utf-8') as f:
            self.configs = json.load(f)
        self.title = title
        self.content = content

    def run(self):

        ring = AlarmMessageBox(self.configs)
        ring.make_up(self.configs,self.title,self.content)
        ring.alert.start()

        



class Master(QWidget):

    def __init__(self):

        super(Master,self).__init__(None)
        self.workers = list()

    def ring(self,title,content):

        with open("./configs.json","r",encoding='utf-8') as f:
            configs = json.load(f)
        ring = AlarmMessageBox(configs)
        ring.make_up(configs,title,content)
        ring.alert.start()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    master = Master()
    process = multiprocessing.Process(target=run_microservice,args=(master,))
    process.start()
    sys.exit(app.exec_())