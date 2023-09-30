import threading
from typing import Optional
from pynput import keyboard
from PyQt6.QtCore import QThread, pyqtSignal
import time
import logging

from config import AIConfig


class AIKeyboardListenerThread(QThread):
    hotkey_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件
    menukey_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件
    exit_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件
    enter_signal = pyqtSignal()  # 定义一个信号，用于传递热键事件

    def __init__(self, stop_flag, config: AIConfig):
        super(AIKeyboardListenerThread, self).__init__()
        self.current_keys = set()  # 用于追踪当前按下的键
        self.last_triggered_time = 0
        self.stop_flag = stop_flag
        self.config = config
        self.listener: Optional[keyboard.Listener] = None

    def run(self):
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        with self.listener as listener:
            listener.join()

    def stop(self):
        self.listener.stop()

    def on_press(self, key):
        try:
            self.current_keys.add(key.char)
        except AttributeError:
            self.current_keys.add(str(key))

        current_time = time.time()
        if current_time - self.last_triggered_time < 1:
            return
        if (
            self.config.generation_key1 in self.current_keys
            and self.config.generation_key2 in self.current_keys
        ):
            self.hotkey_signal.emit()  # 发送热键信号
            self.last_triggered_time = current_time
        if (
            "Key.cmd" in self.current_keys or "Key.ctrl" in self.current_keys
        ) and "k" in self.current_keys:
            self.menukey_signal.emit()  # 发送热键信号
            self.last_triggered_time = current_time
        if "Key.esc" in self.current_keys:
            self.exit_signal.emit()
            self.stop_flag.set()
        if "Key.enter" in self.current_keys:
            self.enter_signal.emit()

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
