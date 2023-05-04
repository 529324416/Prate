
from PyQt5.QtWidgets import QWidget, QApplication
import multiprocessing as mp
import sys
from messagebox import AlarmMessageBox

def _create_message_box(title, information):

    app = QApplication(sys.argv)
    box = AlarmMessageBox(titleFont="汉仪铸字木头人W", contentFont="汉仪铸字木头人W")
    
    box.set_infos(title, information)
    box.fadeup()
    sys.exit(app.exec_())



if __name__ == "__main__":
    # mp.freeze_support()
    p = mp.Process(target=_create_message_box, args=("这是一个很长很长的标题内容", "这是一个简单的测试这是一个简单的测试这是一个简单的测试这"))
    p.start()
