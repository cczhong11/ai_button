from pynput import mouse
from PyQt6.QtCore import QThread, pyqtSignal


class MouseListenerThread(QThread):
    # Add class docstring here
    mouse_click_signal = pyqtSignal(int, int)

    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if not pressed:  # 只在鼠标释放时发送信号
            self.mouse_click_signal.emit(int(x), int(y))
