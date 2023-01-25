# name: AlaramWindow.py
# time: 2022.12.20
# desc: build up a simple window with PyQt5


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ease import EaseFunction
import sys

class StyleNames:
    AlarmMainWindow = "AlarmMainWindow"
    AlarmMainWindowCover = "AlarmMainWindowCover"
    AlarmMainWindowTitle = "AlarmMainWindowTitle"
    AlarmMainWindowContent = "AlarmMainWindowContent"
    AlarmMainWindowIcon = "AlarmMainWindowIcon"

class AlarmMessageBox(QWidget):

    def __init__(self, parent=None, 
        textPadding=10, 
        shadowArea=(16, 16), 
        shadowOffset=(0, 0), 
        shadowBlurRadius=20, 
        shadowColor="#131317",
        titleFont="楷体",
        titleFontSize=20,
        contentFont="楷体",
        contentFontSize=14,
        ):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.shadowOffset = shadowOffset
        self.textPadding = textPadding
        self.containerPadding = QSize(*shadowArea) * 2

        # about container
        self.container = QLabel(self)
        self.container.setObjectName(StyleNames.AlarmMainWindow)
        self.container.move(*shadowArea)
        effects = QGraphicsDropShadowEffect()
        effects.setOffset(QPoint(*shadowOffset))
        effects.setBlurRadius(shadowBlurRadius)
        effects.setColor(QColor(shadowColor))
        self.container.setGraphicsEffect(effects)

        # about container_cover
        self.container_cover = QLabel(self.container)
        self.container_cover.setObjectName(StyleNames.AlarmMainWindowCover)

        # about title
        self.title = QLabel(self.container_cover)
        self.title.setObjectName(StyleNames.AlarmMainWindowTitle)
        self.title.move(textPadding, textPadding)
        self.title.setFont(QFont(titleFont, titleFontSize))

        # about content
        self.content = QLabel(self.container_cover)
        self.content.setObjectName(StyleNames.AlarmMainWindowContent)
        self.content.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.content.setFont(QFont(contentFont, contentFontSize))
        self.content.setWordWrap(True)

    def render(self, title:str, content:str):
        '''render title and content'''

        self.title.setText(title)
        metrices = QFontMetrics(self.title.font())
        titleHeight = metrices.height()
        self.title.resize(self.container.width(), titleHeight)
        
        
        self.content.move(self.textPadding, self.textPadding * 2 + titleHeight)
        self.content.resize(self.container_cover.width() - self.textPadding, self.container.height() - titleHeight - self.textPadding * 2)
        self.content.setText(content)

        metrices = QFontMetricsF(self.content.font())
        width = metrices.width(self.content.text())
        print(width / (self.container_cover.width() - self.textPadding * 2))
        print(metrices.height())
        print(self.content.lineWidth())

        # self.content.setWordWrap(True)

    def resizeEvent(self, evt: QResizeEvent) -> None:
        self.container.resize(self.size() - self.containerPadding)
        self.container_cover.resize(self.container.size())
        return super().resizeEvent(evt)
    

app = QApplication(sys.argv)
window = AlarmMessageBox(titleFont="汉仪铸字木头人W",contentFont="汉仪铸字木头人W")
window.show()
window.resize(280 + 32, 400 + 32)
with open("./Res/style.qss",'r',encoding='utf-8') as f:
    window.setStyleSheet(f.read())
window.render("Install Done","这是一个简单的测试这是一个简单的测试这是一个简单的测试这是一个简单的测试这是一个简单的测试")
exit(app.exec_())