# !user/bin/python3
# Auther: Prince Biscuit
# Date: 2024/02/02
# Desc: an easy module based on pyqt5 to implement global message box or tip box

import sys
import json
import math
import queue
import multiprocessing

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QSize, QPoint

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from PyQt5.QtGui import QMouseEvent, QMoveEvent
from PyQt5.QtGui import QFont, QColor

def _thread_func(_craft_window_callback : callable, *args, **kwargs):
    '''wrapper invoke function'''

    _app = QApplication(sys.argv)
    window = _craft_window_callback(*args, **kwargs)
    window.show()
    window.build_tween_animation()
    window.start_tween_animation()
    _app.exec_()

def _invoke_msg_window(_craft_window : callable, *args, **kwargs):
    '''start to show tip window'''

    _process = multiprocessing.Process(target=_thread_func, args=(_craft_window, *args, *kwargs))
    _process.start()

def _lerp(a:float, b:float, p:float) -> float:
    '''linear interpolation
    @param a: the start value
    @param b: the end value
    @param p: the progress, from 0 to 1
    @return: the value after linear interpolation'''

    return a + (b - a) * p

class EaseFunction:
    '''provide some simple tween functions'''

    @staticmethod
    def linear(x:float) -> float:
        return x

    @staticmethod
    def out_expo(x:float) -> float:
        return 1 - math.pow(2, -10 * x)

    @staticmethod
    def out_back(x:float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * math.pow(x - 1, 3) + c1 * math.pow(x - 1, 2)

class EaseType:
    '''mark ease function'''

    LINEAR = 0
    OUT_EXPO = 1
    OUT_BACK = 2

    __functions = [
        EaseFunction.linear,
        EaseFunction.out_expo,
        EaseFunction.out_back
    ]

    @staticmethod
    def get_method(ease_type:int) -> object:
        '''get ease function by ease type
        @param ease_type: the type of ease function
        @return: the ease function, if the ease type is invalid, return linear function'''

        if callable(ease_type):
            return ease_type

        if ease_type < 0 or ease_type >= len(EaseType.__functions):
            return EaseFunction.linear
        return EaseType.__functions[ease_type]


class TweenTimer(QObject):
    '''provide timer based on pyqt5 to implement tween animation'''

    def __init__(self, interval:int = 5) -> None:
        '''init the tween handle
        @param update: the update callback function'''

        super().__init__(None)
        self.timer = QTimer(self)
        self.timer.setInterval(max(1, interval))
        self.timer.timeout.connect(self._update)
        self.__on_update = self.empty_update

    def empty_update(self):
        '''empty callback function'''
        pass

    def _update(self) -> None:
        '''update the tween animation and wait for it to finish'''

        self.__tick += 1
        if self.__tick >= self.__duration:
            self.timer.stop()
            if self.__on_completed != None and callable(self.__on_completed):
                self.__on_completed()
            return
        self.__on_update()

    def start(self, update:object, after_done:object = None, duration : int = 1000) -> None:
        '''start the tween animation
        @param callback: the callback function to update the window
        @param duration: the duration of the animation, in millisecond
        @param interval: the interval of the animation, in millisecond'''

        self.__on_update = update if callable(update) else self.empty_update
        
        duration = max(1, duration)
        self.__on_completed = after_done
        self.__duration = duration // self.timer.interval()
        self.__tick = 0
        self.timer.start()

class _TweenBase:
    '''the specific tween animation'''

    def __init__(self, on_update:object, duration:int = 2000):
        '''init the tween animation
        @param on_update: the update callback function
        @param counter: the duration of the animation( in millisecond )'''

        self.on_update = on_update
        self.on_completed = None
        self._duration = duration
        self.__counter = 0
        self.__counter_reci = 0

    @property
    def duration(self):
        '''get the counter of the tween animation'''

        return self._duration

    def ready(self, interval:int = 5):
        '''ready the tween animation
        @param interval: the interval of the animation, in millisecond'''

        interval = max(interval , 1)
        self.__counter = self._duration // interval
        self.__counter_reci = 1 / self.__counter
        self.__tick = 0
        
    def set_on_completed(self, on_completed:object = None):
        '''set the callback function when the animation is completed
        @param on_completed: the callback function when the animation is completed'''

        if on_completed != None and callable(on_completed):
            self.on_completed = on_completed
            return
        self.on_completed = None

    def __update(self):
        '''update the tween animation'''

        self.__tick += 1
        if self.__tick >= self.__counter:
            self.on_update(1)
            if self.on_completed != None and callable(self.on_completed):
                self.on_completed()
            return
        self.on_update(self.__tick * self.__counter_reci)

    def run(self):
        '''run the tween animation'''

        self.__update()

class _TweenSequence(_TweenBase):
    '''list of tween animation'''

    def __init__(self):
        '''init the tween animation'''

        super().__init__(self.__update_group, 0)
        self.tweens = []
        self.curmax_dur = 0

    def ready(self, interval: int = 5):
        '''ready the tween animation
        @param interval: the interval of the animation, in millisecond'''

        super().ready(interval)
        for tween in self.tweens:
            tween.ready(interval)

    def append(self, tween: _TweenBase):
        '''append a new tween '''

        self.tweens.append(tween)
        self.curmax_dur = max(self.curmax_dur, tween.duration)
        self._duration = self.curmax_dur

    def __update_group(self, p):
        '''update the tween animation'''

        for tween in self.tweens:
            tween.run()


class TweenAnimation:
    '''the final control element of the tween'''

    def __init__(self, interval:int = 5):
        '''init the tween animation
        @param interval: the interval of the animation, in millisecond'''

        self.__timer = TweenTimer(max(1, interval))
        self.__tweens = list()

    def append(self, tween: _TweenBase):
        '''append a new tween to the last of current animation list'''

        if tween is None:
            return
        self.__tweens.append(tween)

    def append_wait(self, duration:int = 1000):
        '''wait for some seconds'''

        self.append(TweenWait(duration))

    def join(self, tween: _TweenBase):
        '''join a new tween to the last of current animation list
        this tween would run with the previous tween'''

        if tween is None:
            return

        if len(self.__tweens) == 0:
            self.__tweens.append(tween)
            return
        
        last_tween = self.__tweens[-1]
        if isinstance(last_tween, _TweenSequence):
            last_tween.append(tween)
            return
        
        sequence = _TweenSequence()
        sequence.append(last_tween)
        sequence.append(tween)
        self.__tweens[-1] = sequence

    def clear(self):
        '''clear all the tween animation'''

        self.__tweens.clear()

    def play(self, on_animation_done:object = None):
        '''start to play this animation'''

        if len(self.__tweens) == 0:
            return
        
        anim_queue = queue.Queue()
        for tween in self.__tweens:
            anim_queue.put(tween)

        def __next():
            '''callback when a single animation is done'''

            if anim_queue.empty():
                if on_animation_done != None and callable(on_animation_done):
                    on_animation_done()
                return
            
            _anim = anim_queue.get()
            _anim.ready(self.__timer.timer.interval())
            self.__timer.start( _anim.run, __next, _anim.duration)

        __next()

    def stop(self):
        '''stop the animation'''

        self.__timer.timer.stop()



# class TweenDebug(_TweenBase):
#     '''just use for debug'''

#     def __init__(self, debug_content:str = None, duration = 1000):
#         '''init the tween animation'''

#         super().__init__(self.on_update, duration)
#         self.debug_content = debug_content

#     def on_update(self, p: float):
#         '''update the tween animation
#         @param p: the progress of the animation, from 0 to 1'''

#         print('debug:', self.debug_content, p)

class TweenWait(_TweenBase):
    '''wait for a while'''

    def __init__(self, duration:int = 1000):
        '''init the tween animation'''

        super().__init__(self.on_update, duration)

    def on_update(self, p: float):
        '''do nothing, just for wait
        @param p: the progress of the animation, from 0 to 1'''

        pass

class TweenAlpha(_TweenBase):
    '''control the alpha of target element'''

    @staticmethod
    def to_alpha(alpha_setter:object, from_alpha:float, to_alpha:float, duration:int = 1000, ease_type = EaseType.LINEAR):
        '''create a new tween animation to control the alpha of target element'''

        if not callable(alpha_setter):
            return None
        return TweenAlpha(alpha_setter, from_alpha, to_alpha, duration=duration, ease_type=ease_type)
    
    @staticmethod
    def fade_out(alpha_setter:object, duration:int = 1000, ease_type = EaseType.LINEAR):
        '''create a new tween animation to fade out the target element'''

        if not callable(alpha_setter):
            return None
        return TweenAlpha(alpha_setter, 1, 0, duration=duration, ease_type=ease_type)
    
    @staticmethod
    def fade_in(alpha_setter:object, duration:int = 1000, ease_type = EaseType.LINEAR):
        '''create a new tween animation to fade in the target element'''

        if not callable(alpha_setter):
            return None
        return TweenAlpha(alpha_setter, 0, 1, duration=duration, ease_type=ease_type)

    def __init__(self, alpha_setter:object, from_alpha:float, to_alpha:float, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''init the tween animation'''

        super().__init__(self.on_update, duration)
        self._alpha_setter = alpha_setter if callable(alpha_setter) else self.empty_setter
        self._from_alpha = from_alpha
        self._to_alpha = to_alpha
        self._ease = EaseType.get_method(ease_type)

    def empty_setter(self, alpha:float):
        '''empty callback function'''
        pass

    def on_update(self, p: float):
        '''update the tween animation'''

        self._alpha_setter(_lerp(self._from_alpha, self._to_alpha, self._ease(p)))

class TweenMove(_TweenBase):
    '''control the position of target element'''

    @staticmethod
    def to_pos(pos_setter:object, from_pos:tuple, to_pos:tuple, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to control the position of target element'''

        if not callable(pos_setter):
            return None
        return TweenMove(pos_setter, from_pos, to_pos, duration=duration, ease_type=ease_type)

    def __init__(self, pos_setter:object, from_pos:tuple, to_pos:tuple, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''init the tween animation'''

        super().__init__(self.on_update, duration)
        self._pos_setter = pos_setter if callable(pos_setter) else self.empty_setter
        self._from_pos = from_pos
        self._to_pos = to_pos
        self._ease = EaseType.get_method(ease_type)

    def empty_setter(self, pos:tuple):
        '''empty callback function'''
        pass

    def on_update(self, p: float):
        '''update the tween animation'''

        t = self._ease(p)
        x = _lerp(self._from_pos[0], self._to_pos[0], t)
        y = _lerp(self._from_pos[1], self._to_pos[1], t)
        self._pos_setter(int(x), int(y))








class QtTweenHelper:
    '''provide some fast api to control the animation of qt element'''

    @staticmethod
    def fade_out(window:QWidget, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to fade out the target element'''

        if window is None:
            return None
        return TweenAlpha.fade_out(window.setWindowOpacity, duration, ease_type)

    @staticmethod
    def fade_in(window:QWidget, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to fade in the target element'''

        if window is None:
            return None
        return TweenAlpha.fade_in(window.setWindowOpacity, duration, ease_type)

    @staticmethod
    def move_up_here(window:QWidget, distance:int = 100, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to move up the target element'''

        if window is None:
            return None
        
        currentPos = window.pos()
        x = currentPos.x()
        y = currentPos.y()
        return TweenMove.to_pos(window.move, (x, y + distance), (x, y), duration, ease_type)
    
    @staticmethod
    def move_up(window:QWidget, distance:int = 100, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to move up the target element'''

        if window is None:
            return None
        
        currentPos = window.pos()
        x = currentPos.x()
        y = currentPos.y()
        return TweenMove.to_pos(window.move, (x, y), (x, y - distance), duration, ease_type)

    @staticmethod
    def move_down_here(window:QWidget, distance:int = 100, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to move down the target element'''

        if window is None:
            return None
        currentPos = window.pos()
        x = currentPos.x()
        y = currentPos.y()
        return TweenMove.to_pos(window.move, (x, y - distance), (x, y), duration, ease_type)
    
    @staticmethod
    def move_down(window:QWidget, distance:int = 100, duration:int = 1000, ease_type:int = EaseType.LINEAR):
        '''create a new tween animation to move down the target element'''

        if window is None:
            return None
        currentPos = window.pos()
        x = currentPos.x()
        y = currentPos.y()
        return TweenMove.to_pos(window.move, (x, y), (x, y + distance), duration, ease_type)

class PrateStyleUtils:

    def make_color(colorInfo) -> str:
        '''given a color information and return style string'''

        if isinstance(colorInfo, tuple):
            if len(tuple) == 3:
                return f"rgb{colorInfo}"
            elif len(tuple) == 4:
                return f"rgba{colorInfo}"
            else:
                raise ValueError(f"invalid color tuple {colorInfo}")
            
        elif isinstance(colorInfo, str):
            if not colorInfo.startswith("#"):
                return "#" + colorInfo
            else:
                return colorInfo

class PrateName:

    Window = "PrateWindow"
    Content = "PrateContent"
    Overlay = "PrateOverlay"
    Title = "PrateTitle"
    Info = "PrateInfo"

class PrateContentBase(QLabel):
    '''add overlay to prate content'''

    def __init__(self, parent: QWidget, size: QSize):
        '''init the prate content'''

        super().__init__(parent)
        self.setObjectName(PrateName.Content)
        self.resize(size)
        
        self._overlay = QLabel(self)
        self._overlay.setObjectName(PrateName.Overlay)
        self._overlay.move(0, 0)
        self._overlay.resize(size)

    @property
    def overlay(self):
        return self._overlay

class PrateContent(PrateContentBase):
    '''the main content of prate message box'''

    def __init__(self, 
        parent: QWidget, 
        size: QSize,
        has_title = True, 
        padding = 12, 
        gap:int = 8, 
        title_font: QFont = None, 
        info_font: QFont = None):
        '''initialize prate main content'''

        super().__init__(parent, size)
        self._padding_size = QSize(padding * 2, padding * 2)
        self._padding_offset = QPoint(padding, padding)
        self._gap = gap
        self._has_title = has_title

        # about message title
        if self._has_title:
            self.title = QLabel(self.overlay)
            self.title.setObjectName(PrateName.Title)
            if title_font != None: 
                self.title.setFont(title_font)
            self.title.move(self.title_pos)
            self.title.resize(self.title_size)

        # about message description
        self.info = QLabel(self.overlay)
        self.info.setObjectName(PrateName.Info)
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignmentFlag.AlignTop)

        if info_font != None:
            self.info.setFont(info_font)
        self.info.move(self.info_pos)
        self.info.resize(self.info_size)

    @property
    def title_pos(self):
        '''get the position of title'''

        return self._padding_offset
    
    @property
    def title_size(self):
        '''get the size of title'''

        fontMetrics = self.title.fontMetrics()
        return QSize(self.width() - self._padding_size.width(), fontMetrics.height())
    
    @property
    def info_pos(self):
        '''get the position of info'''

        if self._has_title:
            return self.title.pos() + QPoint(0, self.title.height() + self._gap)
        return self._padding_offset
    
    @property
    def info_size(self):
        '''get the size of info'''

        if self._has_title:
            return QSize(self.title.width(), self.height() - self.title.height() - self._padding_size.height() - self._gap)
        return self.size() - self._padding_size
        
    def set_content(self, title, info):
        '''set title and info'''

        if self._has_title:
            fontMetrics = self.title.fontMetrics()
            text = fontMetrics.elidedText(title, Qt.TextElideMode.ElideRight, self.title_size.width())
            self.title.setText(text)

        fontMetrics = self.info.fontMetrics()
        lineHeight = fontMetrics.lineSpacing() + fontMetrics.lineWidth()
        lineCapacity = math.floor(self.info_size.height() / lineHeight)
        totalWidth = lineCapacity * self.info.width()
        info = fontMetrics.elidedText(info, Qt.TextElideMode.ElideRight, totalWidth)
        self.info.setText(info)

class PrateWindow(QWidget):
    '''provide base window of prate'''

    def __init__(self,
        window_size = (280, 400),
        padding = 10,
        content_padding = 12,
        content_gap = 8,
        has_title = True,
        title_font_name = "Microsoft YaHei",
        title_font_size = 16,
        info_font_name = "Microsoft YaHei",
        info_font_size = 12,
    ):
        '''init the window'''

        super().__init__(None)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(*window_size)
        self._padding_offset = QPoint(padding, padding)
        self._padding_size = QSize(padding * 2, padding * 2)

        # about content
        self.content = PrateContent(
            self, 
            self.size() - self._padding_size,
            has_title, 
            content_padding, 
            content_gap, 
            QFont(title_font_name, title_font_size), 
            QFont(info_font_name, info_font_size)
        )

        self.content.move(self._padding_offset)
        self.content.resize(self.size() - self._padding_size)
        self.anim = None
    
    def build_tween_animation(self):
        '''build the tween animation'''

        self.anim = TweenAnimation()
        self.anim.append(QtTweenHelper.fade_in(self, 600))
        self.anim.join(QtTweenHelper.move_up_here(self, 100, 600, EaseType.OUT_EXPO))

        self.anim.append_wait(4000)
        self.anim.append(QtTweenHelper.fade_out(self, 450))
        self.anim.join(QtTweenHelper.move_down(self, 100, 600, EaseType.LINEAR))

    def start_tween_animation(self):
        self.anim.play(self.close)
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        self.anim.stop()
        self.close()

    def moveEvent(self, a0: QMoveEvent) -> None:
        self.setWindowTitle(str(a0.pos().y()))
        return super().moveEvent(a0)

    def set_infos(self, title: str, content:str):
        '''set the title and content of the window'''

        self.content.set_content(title, content)

    @property
    def visible_size(self):
        '''get the real size of the window'''

        return self.size() - self._padding_size



class ScreenPosition:

    LeftBottom = "leftbottom"
    LeftTop = "lefttop"
    RightBottom = "rightbottom"
    RightTop = "righttop"
    Center = "center"

    def get_pos(size, flag:str):
        

        if isinstance(size, list) or isinstance(size, tuple):
            size = QSize(*size)

        if flag.lower() == ScreenPosition.LeftBottom:
            return ScreenPositionUtils.get_left_bottom(size)
        
        if flag.lower() == ScreenPosition.LeftTop:
            return ScreenPositionUtils.get_left_top(size)
        
        if flag.lower() == ScreenPosition.RightBottom:
            return ScreenPositionUtils.get_right_bottom(size)
        
        if flag.lower() == ScreenPosition.RightTop:
            return ScreenPositionUtils.get_right_top(size)
        
        if flag.lower() == ScreenPosition.Center:
            return ScreenPositionUtils.get_center(size)
        
        return QPoint()




class ScreenPositionUtils:
    '''provide some utils to get the position of screen'''

    @staticmethod
    def get_left_bottom(size: QSize, padding: QSize = QSize(12, 12)):
        
        screen_size = QApplication.primaryScreen().size()
        return QPoint(padding.width(), screen_size.height() - size.height() - padding.height())
    
    @staticmethod
    def get_left_top(size: QSize, padding: QSize = QSize(12, 12)):
        
        return QPoint(padding.width(), padding.height())
    
    @staticmethod
    def get_right_bottom(size: QSize, padding: QSize = QSize(12, 12)):
            
        screen_size = QApplication.primaryScreen().size()
        return QPoint(screen_size.width() - size.width() - padding.width(), screen_size.height() - size.height() - padding.height())
    
    @staticmethod
    def get_right_top(size: QSize, padding: QSize = QSize(12, 12)):
        
        screen_size = QApplication.primaryScreen().size()

        return QPoint(screen_size.width() - size.width() - padding.width(), padding.height())
    
    @staticmethod
    def get_center(size: QSize):
        
        screen_size = QApplication.primaryScreen().size()
        return QPoint((screen_size.width() - size.width()) // 2, (screen_size.height() - size.height()) // 2)

class PrateWindowAppearanceConfigure:
    '''configure the appearance of prate window'''

    @staticmethod
    def save_template(filepath = "./template.json"):
        configure = PrateWindowAppearanceConfigure.white()
        PrateWindowAppearanceConfigure.save(configure, filepath)

    @staticmethod
    def save(style, filepath):
        '''save style to json'''

        configure = {}
        configure.setdefault("window-size", style.window_size)
        configure.setdefault("screen-pos", style.screen_pos)
        configure.setdefault("border-radius", style.border_radius)
        configure.setdefault("background-image", style.background_image)
        configure.setdefault("overlay-color", style.overlay_color)
        configure.setdefault("title-color", style.title_color)
        configure.setdefault("info-color", style.info_color)
        configure.setdefault("padding", style.padding)
        configure.setdefault("content-padding", style.content_padding)
        configure.setdefault("content-gap", style.content_gap)
        configure.setdefault("has-title", style.has_title)
        configure.setdefault("title-font-name", style.title_font_name)
        configure.setdefault("title-font-size", style.title_font_size)
        configure.setdefault("title-font-style", style.title_font_style)
        configure.setdefault("title-font-bold", style.title_font_bold)
        configure.setdefault("info-font-name", style.info_font_name)
        configure.setdefault("info-font-size", style.info_font_size)
        configure.setdefault("info-font-style", style.info_font_style)
        configure.setdefault("info-font-bold", style.info_font_bold)
        configure.setdefault("shadow-blur-radius", style.shadow_blur_radius)
        configure.setdefault("shadow-x-offset", style.shadow_x_offset)
        configure.setdefault("shadow-y-offset", style.shadow_y_offset)
        configure.setdefault("shadow-color", style.shadow_color)

        with open(filepath, "w", encoding='utf-8') as file:
            file.write(json.dumps(configure, indent=4))

    @staticmethod
    def read(filepath):
        '''read style from json'''

        with open(filepath, "r", encoding='utf-8') as file:
            configure = json.loads(file.read())

        try:
            return PrateWindowAppearanceConfigure(
                configure["window-size"],
                configure["screen-pos"],
                configure["border-radius"],
                configure["background-image"],
                configure["overlay-color"],
                configure["title-color"],
                configure["info-color"],
                configure["padding"],
                configure["content-padding"],
                configure["content-gap"],
                configure["has-title"],
                configure["title-font-name"],
                configure["title-font-size"],
                configure["title-font-bold"],
                configure["title-font-style"],

                configure["info-font-name"],
                configure["info-font-size"],
                configure["info-font-bold"],
                configure["info-font-style"],
                configure["shadow-blur-radius"],
                configure["shadow-x-offset"],
                configure["shadow-y-offset"],
                configure["shadow-color"]
            )
        except Exception:
            return None

    @staticmethod
    def white():
        return PrateWindowAppearanceConfigure(
            overlay_color="qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(168,237,234,130), stop:1 #fed6e3)",
            title_color="#26203a",
            info_color="#30324d"
        )
    
    @staticmethod
    def dark():
        return PrateWindowAppearanceConfigure(
            overlay_color="#1f202d",
            title_color="#c4c4c4",
            info_color="#969696"
        )

    def __init__(
        self,
        window_size = [280, 400],
        screen_pos = "RightBottom",
        border_radius:int = 16,
        background_image:str = None,
        overlay_color:str = "rgba(0, 0, 0, 0.3)",
        title_color:str = "#c4c4c4",
        info_color:str = "#969696",
        padding:int = 10,
        content_padding:int = 12,
        content_gap:int = 8,
        has_title:bool = True,

        title_font_name:str = "Microsoft YaHei",
        title_font_size:int = 16,
        title_font_bold:bool = False,
        title_font_style:str = "normal",

        info_font_name:str = "Microsoft YaHei",
        info_font_size:int = 12,
        info_font_bold:bool = False,
        info_font_style:str = "normal",

        shadow_blur_radius:int = 15,
        shadow_x_offset:int = 4,
        shadow_y_offset:int = 4,
        shadow_color:list = [ 0, 0, 0, 120 ]
    ):
        '''init the configure'''

        self.window_size = window_size
        self.screen_pos = screen_pos
        self.border_radius = border_radius
        self.background_image = background_image
        self.overlay_color = overlay_color
        self.title_color = title_color
        self.info_color = info_color
        self.padding = padding
        self.content_padding = content_padding
        self.content_gap = content_gap
        self.has_title = has_title
        self.title_font_name = title_font_name
        self.title_font_size = title_font_size
        self.title_font_bold = title_font_bold
        self.title_font_style = title_font_style
        self.info_font_name = info_font_name
        self.info_font_size = info_font_size
        self.info_font_bold = info_font_bold
        self.info_font_style = info_font_style
        self.shadow_blur_radius = shadow_blur_radius
        self.shadow_x_offset = shadow_x_offset
        self.shadow_y_offset = shadow_y_offset
        self.shadow_color = shadow_color

    def craft_window(self):
        '''craft the window'''

        qss = f'''
#{PrateName.Window}{{
    border-radius: {self.border_radius}px;
    background-image: url({self.background_image});
    background-repeat: no-repeat;
    background-position: center;
}}
#{PrateName.Overlay}{{
    border-radius: {self.border_radius}px;
    background-color: {self.overlay_color};
}}
#{PrateName.Title}{{
    {"font-weight: bold;" if self.title_font_bold else ""}
    font-style: {self.title_font_style};
    color: {self.title_color};
}}
#{PrateName.Info}{{
    {"font-weight: bold;" if self.info_font_bold else ""}
    font-style: {self.info_font_style};
    color: {self.info_color};
}}
        '''

        shadowColor = QColor(*self.shadow_color)
        shadow = QGraphicsDropShadowEffect(blurRadius=self.shadow_blur_radius, xOffset=self.shadow_x_offset, yOffset=self.shadow_y_offset, color=shadowColor)
        window = PrateWindow(
            window_size=tuple(self.window_size),
            padding=self.padding,
            content_padding=self.content_padding,
            content_gap=self.content_gap,
            has_title=self.has_title,
            title_font_name=self.title_font_name,
            title_font_size=self.title_font_size,
            info_font_name=self.info_font_name,
            info_font_size=self.info_font_size
        )
        window.content.setGraphicsEffect(shadow)
        window.move(ScreenPosition.get_pos(window.size(), self.screen_pos))
        window.setStyleSheet(qss)
        return window

    
# def get_window_crafter(title:str, content:str, configure_path:str):
    
#     configure = PrateWindowAppearanceConfigure.read(configure_path)
#     if configure == None: configure = PrateWindowAppearanceConfigure.white()

#     def _craft_window():
#         window = configure.craft_window()
#         window.set_infos(title, content)
#         return window
    
#     return _craft_window
    

class Prate:
    '''provide some simple api to show message box'''

    def __init__(self, configure:str|PrateWindowAppearanceConfigure):
        '''init the prate
        @param configure: the configure of the prate window'''

        if isinstance(configure, str):
            self.configure = PrateWindowAppearanceConfigure.read(configure)
            if self.configure == None: 
                self.configure = PrateWindowAppearanceConfigure.white()
        elif isinstance(configure, PrateWindowAppearanceConfigure):
            self.configure = configure
        else:
            self.configure = PrateWindowAppearanceConfigure.white()

    def _craft_window(self, title:str = "", content:str = ""):
        '''ring the message box'''

        window = self.configure.craft_window()
        window.set_infos(title, content)
        return window
    
    def ring(self, title:str = "", content:str = ""):
        '''ring the message box'''

        _invoke_msg_window(self._craft_window, title, content)


def craft_window(title:str, content:str, configure_path:str):
    '''craft the window'''

    global configure
    if configure is None:
        print(configure_path)
        configure = PrateWindowAppearanceConfigure.read(configure_path)
        if configure == None: configure = PrateWindowAppearanceConfigure.white()

    window = configure.craft_window()
    window.set_infos(title, content)
    return window

def ring(title = "", content = ""):
    '''ring the message box'''

    _invoke_msg_window(craft_window, title, content, "default.json")


if __name__ == '__main__':

    prate = Prate("default.json")
    prate.ring("hello", "world")

    # note that: the prate.ring function can be used in other application's main loop
    #            a = 0
    #            while 1:
    #                a += 1
    #                if a % 3 == 0:
    #                   prate.ring("hello", "world")
    #                time.sleep(1)