from pynput import mouse
from PyQt6.QtCore import QThread, pyqtSignal


class MouseListenerThread(QThread):
    # Add class docstring here

    def run(self, clicked_event):
        self.clicked_event = clicked_event
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if not pressed:  # 只在鼠标释放时发送信号
            self.clicked_event.set()
