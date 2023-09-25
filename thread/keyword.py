from pynput import keyboard
from PyQt6.QtCore import QThread, pyqtSignal


class AIKeyboardListenerThread(QThread):
    hotkey_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件
    menukey_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件
    exit_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件

    def __init__(self):
        super(AIKeyboardListenerThread, self).__init__()
        self.current_keys = set()  # 用于追踪当前按下的键

    def run(self):
        with keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        ) as listener:
            listener.join()

    def on_press(self, key):
        try:
            self.current_keys.add(key.char)
        except AttributeError:
            self.current_keys.add(str(key))
        # 检查是否按下了Command+K组合键（在Mac上）或Ctrl+K（在Windows和Linux上）
        if (
            "Key.cmd" in self.current_keys or "Key.ctrl" in self.current_keys
        ) and "`" in self.current_keys:
            self.hotkey_signal.emit()  # 发送热键信号
        if (
            "Key.cmd" in self.current_keys or "Key.ctrl" in self.current_keys
        ) and "k" in self.current_keys:
            self.menukey_signal.emit()  # 发送热键信号
        if "Key.esc" in self.current_keys:
            self.exit_signal.emit()

    def on_release(self, key):
        try:
            self.current_keys.remove(key.char)
        except AttributeError:
            try:
                self.current_keys.remove(str(key))
            except KeyError:
                pass
        except KeyError:
            self.current_keys.clear()
