# name: AlaramWindow.py
# time: 2022.12.20
# desc: build up a simple window with PyQt5


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from messagebox_animation import FadeUpAnimation
import sys

class StyleNames:
    AlarmMainWindow = "AlarmMainWindow"
    AlarmMainWindowCover = "AlarmMainWindowCover"
    AlarmMainWindowTitle = "AlarmMainWindowTitle"
    AlarmMainWindowContent = "AlarmMainWindowContent"
    AlarmMainWindowIcon = "AlarmMainWindowIcon"

defaultStyle = '''
#AlarmMainWindow{
    border-radius: 12px;
    border: none;
    background-image: url(./Res/D0gCaFrW0AIs--I.png);
    background-position: center;
}
#AlarmMainWindowCover{
    border-radius: 10px;
    border: none;
    background-color:qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(26,28,44,130), stop:1 #1a1c2c)
}
#AlarmMainWindowTitle{
    color: #FFFDE3;
}
#AlarmMainWindowContent{
    color: #8e8e9f;
}
'''

def screen_position_rb(w:QWidget, rightPadding = 16, bottomPadding = 32) -> QPoint:
    '''return the right bottom point of the screen'''

    screen = QApplication.primaryScreen()
    _size = screen.size()
    return QPoint(_size.width() - w.width() - rightPadding, _size.height() - w.height() - bottomPadding)

class AlarmMessageBox(QWidget):

    def __init__(
        self,
        parent=None, 
        textPadding=10,
        size=(312, 432),
        shadowArea=(16, 16), 
        shadowOffset=(0, 0), 
        shadowBlurRadius=20, 
        shadowColor="#131317",
        titleFont="楷体",
        titleFontSize=16,
        contentFont="楷体",
        contentFontSize=14,
        styleSheet=defaultStyle
    ):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.shadowOffset = shadowOffset
        self.textPadding = textPadding
        self.containerPadding = QSize(*shadowArea) * 2
        self.setStyleSheet(styleSheet)

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

        self.resize(*size)
        self.update_geometry()

        self.anim = None
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def set_infos(self, title:str, info:str):
        '''render title and content'''

        metrices = QFontMetrics(self.title.font())
        self.title.setText(metrices.elidedText(title, Qt.ElideRight, self.title.width() - self.textPadding * 2))
        self.content.setText(info)

    def fadeup(self):
        '''显示窗体'''

        if self.isHidden():
            self.show()
        self.move(screen_position_rb(self, 8, 48))
        self.anim = FadeUpAnimation(self)
        self.anim.show()

    def update_geometry(self):
        '''update geometry of the window'''

        self.container.resize(self.size() - self.containerPadding)
        self.container_cover.resize(self.container.size())
        self.title.resize(self.container.width() - self.textPadding, self.title.height())
        self.content.move(self.title.x(), self.title.y() + self.title.height() + self.textPadding)
        self.content.resize(self.title.width(), self.container.height() - self.content.y() - self.textPadding)