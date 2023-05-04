
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QObject, QPoint
from ease import EaseFunction


class _AnimatorTimer(QObject):
    '''similar to QTimer, but add some useful functions'''

    def __init__(self, interval = 5):
        super().__init__(None)
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.__update)

        self.current_tick = 0
        self.duration = 0
        self.__callback_on_update = self.__empty_update

    def __empty_update(self, process: float):
        pass

    def set_callback(self, cb:callable):
        self.__callback_on_update = cb

    @property
    def process(self) -> float:
        return self.current_tick / self.duration

    def start_animator(self, duration):
        '''开始动画'''

        self.current_tick = 0
        self.duration = duration // self.timer.interval()
        self.timer.start(5)

    def __update(self) -> bool:
        '''update timer'''

        self.current_tick += 1        
        self.__callback_on_update(self.process)
        if self.current_tick >= self.duration:
            self.current_tick = self.duration
            self.timer.stop()
            return True
        return False
    

class FadeUpAnimation:
    '''对某个widget进行控制'''

    def __init__(self, widget: QWidget, dur_show = 500, dur_hide = 500, dur_wait = 3000, interval = 5, popDst = 200):

        self.widget = widget
        self.dur_show = dur_show
        self.dur_hide = dur_hide
        self.dur_wait = dur_wait
        self.interval = interval
        self.popDst = popDst

        self.timer = _AnimatorTimer(interval)
        self.target_pos = widget.pos()
        self.hide_pos = widget.pos() + QPoint(0, popDst)

        self.state = 0

    @property
    def is_showing(self) -> bool:
        return self.state == 0
    
    @property
    def is_waiting(self) -> bool:
        return self.state == 1
    
    @property
    def is_hiding(self) -> bool:
        return self.state == 2

    def reset(self, state):
        '''reset window to ready state'''

        self.state = state
        if state == 0:
            self.widget.setWindowOpacity(0)
            self.widget.move(self.hide_pos)
        else:
            self.widget.setWindowOpacity(1)
            self.widget.move(self.target_pos)

    def skip(self):
        '''skip left waiting time'''

        if self.is_showing:
            return

        if self._is_waiting:
            self._hide()

    def show(self):
        '''start to play show animation'''

        def __tick(process):
            '''show animation'''

            self.widget.setWindowOpacity(process)
            _twist = EaseFunction.out_expo(process)
            self.widget.move(self.hide_pos - QPoint(0, int(self.popDst * _twist)))
            if process >= 1.0:
                self._wait()

        self.reset(0)
        self.timer.set_callback(__tick)
        self.timer.start_animator(self.dur_show)

    def _wait(self):
        '''wait for hide'''

        def __tick(process):
            '''wait for hide'''

            if process >= 1.0:
                self._hide()

        self.reset(1)
        self.timer.set_callback(__tick)
        self.timer.start_animator(self.dur_wait)

    def _hide(self):
        '''start to play hide animation'''

        def __tick(process):
            '''hide animation'''

            self.widget.setWindowOpacity(1 - process)
            _twist = EaseFunction.out_expo(process)
            self.widget.move(self.target_pos + QPoint(0, int(self.popDst * _twist)))
            if process >= 1.0:
                self.widget.close()

        self.reset(2)
        self.timer.set_callback(__tick)
        self.timer.start_animator(self.dur_hide)