# startup a process to run a qt window

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import time
from multiprocessing import Process

class WindowThread(QThread):
    def __init__(self):
        super().__init__(None)
        
    def run(self) -> None:
        self.window = QWidget(None)
        self.window.resize(300, 300)
        self.window.setWindowTitle("test window")
        self.window.show()

app = QApplication(sys.argv)
thread = WindowThread()
thread.start()
sys.exit(app.exec_())