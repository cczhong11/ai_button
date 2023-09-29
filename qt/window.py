import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QRect
import time
from pynput.keyboard import Controller, Key

from LLM.chatgpt import get_openai_response
import threading
import subprocess
import sys

keyboard = Controller()


def change_window():
    with keyboard.pressed(Key.cmd if sys.platform == "darwin" else Key.ctrl):
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)


def copy(change_window_flag=True):
    if change_window_flag:
        change_window()
    time.sleep(0.1)
    with keyboard.pressed(Key.cmd if sys.platform == "darwin" else Key.ctrl):
        keyboard.press("c")
        keyboard.release("c")
    time.sleep(0.5)


def paste():
    with keyboard.pressed(Key.cmd if sys.platform == "darwin" else Key.ctrl):
        keyboard.press("v")
        keyboard.release("v")


def get_selected_text(change_window_flag=True):
    copy(change_window_flag)
    return subprocess.check_output(["pbpaste"]).decode("utf-8")


class AIBubble:
    def __init__(self, stop_flag):
        self.app = QApplication([])
        self.summary_button = self.create_button("总结", self.summary_text)
        self.prompt_button = self.create_button("AI", self.generate_text)
        self.init_text_input()
        self.init_text_edit()
        self.init_layout()
        self.init_window()
        self.active = False
        self.keyboard = Controller()

        self.stop_flag = stop_flag

    def init_text_input(self):
        self.text_input = QLineEdit()

    def init_text_edit(self):
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.hide()

    def init_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.summary_button)
        self.layout.addWidget(self.prompt_button)
        self.layout.addWidget(self.text_edit)

    def init_window(self):
        self.window = QWidget()
        self.window.setLayout(self.layout)
        self.window.hide()
        self.window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.window.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.window.hide()

    def enter_key_generate_text(self):
        if self.text_input.text() == "":
            return
        gen = get_openai_response(self.text_input.text(), stream=True)
        self.window.hide()
        self.active = False
        change_window()
        self.run_stream(gen)
        self.text_input.setText("")

    def create_button(self, text, func):
        button = QPushButton(text)
        button.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(func)
        return button

    def exit_generation(self):
        pass

    def generate_text(self):
        print("generate_text ...")
        self.toggle_text_edit(
            "", paste_result=False, stream=True, change_window_flag=False
        )

    def toggle_text_edit(
        self, prefix_prompt="", paste_result=True, stream=False, change_window_flag=True
    ):
        if not isinstance(prefix_prompt, str):
            prefix_prompt = ""
        if self.text_edit.isHidden():
            selected_text = get_selected_text(change_window_flag=change_window_flag)
            result = ""
            if stream:
                gen = get_openai_response(
                    f"{prefix_prompt}{selected_text}", stream=True
                )
                self.run_stream(gen)
            else:
                result = get_openai_response(f"{prefix_prompt}{selected_text}")
                self.text_edit.setText(result)
                self.text_edit.show()
            if paste_result:
                process = subprocess.Popen(
                    "pbcopy", universal_newlines=True, stdin=subprocess.PIPE
                )
                process.communicate(input=result)
                paste()
        else:
            self.text_edit.hide()
        self.window.adjustSize()

    def run_stream(self, gen):
        for response in gen:
            delta = response.choices[0].delta
            if not delta or self.stop_flag.is_set():
                self.stop_flag.clear()
                gen.close()
                break
            for char in delta.content:
                if char == "\n":
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                    continue
                if self.stop_flag.is_set():
                    self.stop_flag.clear()
                    break
                keyboard.press(char)
                keyboard.release(char)
            time.sleep(0.01)

    def summary_text(self):
        prefix_prompt = "你只会说中文，用100个汉字总结："
        self.toggle_text_edit(prefix_prompt, False)

    def move_button(self, x, y):
        rect = QRect(
            self.window.x(), self.window.y(), self.window.width(), self.window.height()
        )

        if not rect.contains(x, y):
            self.window.move(x + 20, y - 50)
            if self.active:
                self.window.show()

    def toggle_window(self):
        if self.window.isHidden():
            self.active = True
            self.window.show()
            self.window.adjustSize()  # 调整窗口大小
        else:
            self.window.hide()
            self.active = False
