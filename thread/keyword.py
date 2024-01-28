import threading
from typing import Optional
from pynput import keyboard
from PyQt6.QtCore import QThread, pyqtSignal
import time
import logging

from config import AIConfig
from logger_util import logger


class AIKeyboardListenerThread(QThread):
    hotkey_signal = pyqtSignal()

    def __init__(self, stop_flag, current_generation, config: AIConfig):
        super(AIKeyboardListenerThread, self).__init__()
        self.current_keys = set()
        self.last_triggered_time = 0
        self.stop_flag = stop_flag
        self.current_generation = current_generation
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
            self.hotkey_signal.emit()
            logger.info(f"AI generation is triggered")
            self.last_triggered_time = current_time

        if "Key.esc" in self.current_keys and self.current_generation.is_set():
            self.stop_flag.set()

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
