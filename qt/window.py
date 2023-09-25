from PyQt6.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QRect
import time
from pynput.keyboard import Controller, Key

from LLM.chatgpt import get_openai_response

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
    time.sleep(0.1)


def paste():
    with keyboard.pressed(Key.cmd if sys.platform == "darwin" else Key.ctrl):
        keyboard.press("v")
        keyboard.release("v")


def get_selected_text(change_window_flag=True):
    copy(change_window_flag)
    return subprocess.check_output(["pbpaste"]).decode("utf-8")


class AIBubble:
    def __init__(self):
        self.app = QApplication([])
        self.summary_button = self.create_button("总结", self.summary_text)
        self.prompt_button = self.create_button("AI", self.generate_text)
        self.init_text_edit()
        self.init_layout()
        self.init_window()
        self.active = False
        self.keyboard = Controller()
        self.stop_generation = False

    def init_text_edit(self):
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.hide()

    def init_layout(self):
        self.layout = QVBoxLayout()
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

    def create_button(self, text, func):
        button = QPushButton(text)
        button.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(func)
        return button

    def exit_generation(self):
        self.stop_generation = True

    def generate_text(self):
        self.toggle_text_edit("", False, True, change_window_flag=False)

    def toggle_text_edit(
        self, prefix_prompt="", paste_result=True, stream=False, change_window_flag=True
    ):
        if not isinstance(prefix_prompt, str):
            prefix_prompt = ""
        if self.text_edit.isHidden():
            selected_text = get_selected_text(change_window_flag=change_window_flag)
            result = ""
            if stream:
                for response in get_openai_response(
                    f"{prefix_prompt}{selected_text}", stream=True
                ):
                    delta = response.choices[0].delta
                    if not delta or self.stop_generation:
                        self.stop_generation = False
                        break
                    for char in delta.content:
                        if char == "\n":
                            keyboard.press(Key.enter)
                            keyboard.release(Key.enter)
                            continue
                        if self.stop_generation:
                            self.stop_generation = False
                            break
                        keyboard.press(char)
                        keyboard.release(char)

                        time.sleep(0.1)
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
