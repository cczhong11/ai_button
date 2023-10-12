import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QMenuBar,
    QMenu,
    QDialog,
    QLabel,
    QHBoxLayout,
    QCheckBox,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QRect
import time
from pynput.keyboard import Controller, Key
import os
from LLM.chatgpt import get_openai_response, set_openai_key
import threading
import subprocess
import sys
from playsound import playsound
from config import AIConfig, write_config
from thread.keyword import AIKeyboardListenerThread

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
    def __init__(self, config: AIConfig):
        self.app = QApplication([])
        self.summary_button = self.create_button("总结", self.summary_text)
        self.prompt_button = self.create_button("AI", self.generate_text)
        self.config = config
        self.init_text_input()
        self.init_text_edit()
        self.init_layout()
        self.init_window()
        self.init_menu()
        self.active = False
        self.keyboard = Controller()
        self.keyboard_listener = None
        self.stop_flag = threading.Event()

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

    def init_menu(self):
        self.menu_bar = QMenuBar()

        file_menu = QMenu("File")
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.app.quit)
        file_menu.addAction(exit_action)

        self.menu_bar.addMenu(file_menu)

        api_menu = QMenu("设置")
        set_api_action = QAction("设置AI", self.app)
        set_key_board_action = QAction("设置热键", self.app)
        set_api_action.triggered.connect(self.show_api_key_dialog)
        set_key_board_action.triggered.connect(self.set_key_board_dialog)
        api_menu.addAction(set_api_action)
        api_menu.addAction(set_key_board_action)

        self.menu_bar.addMenu(api_menu)

        self.menu_bar.show()
        self.init_api_dialog()
        self.init_keyboard_dialog()

    def init_api_dialog(self):
        api_key_input = QLineEdit()
        api_key_input.setMinimumWidth(200)
        api_key_input.setText(self.config.openai_api_key)
        streaming_checkbox = QCheckBox("流式输出")
        streaming_checkbox.setObjectName("streaming")
        streaming_checkbox.setChecked(self.config.streaming)
        sound_checkbox = QCheckBox("播放音效")
        sound_checkbox.setObjectName("sound")
        sound_checkbox.setChecked(self.config.play_sound)
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.set_api_key)

        exit_button = QPushButton("退出")
        exit_button.clicked.connect(self.exit_dialog)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(exit_button)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("设置AI"))
        layout.addWidget(api_key_input)
        layout.addWidget(streaming_checkbox)
        layout.addWidget(sound_checkbox)
        layout.addLayout(button_layout)

        self.api_dialog = QDialog()
        self.api_dialog.setWindowTitle("Set API")
        self.api_dialog.setLayout(layout)
        self.api_dialog.hide()

    def init_keyboard_dialog(self):
        keyboard_input = QLineEdit()
        keyboard_input.setMinimumWidth(20)
        keyboard_input.setObjectName("generation_key1")
        keyboard_input.setText(self.config.generation_key1)
        keyboard_input2 = QLineEdit()
        keyboard_input2.setMinimumWidth(20)
        keyboard_input2.setObjectName("generation_key2")
        keyboard_input2.setText(self.config.generation_key2)
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.set_keyboard)

        exit_button = QPushButton("退出")
        exit_button.clicked.connect(self.exit_dialog)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(exit_button)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("启动AI按键1:"))
        layout.addWidget(keyboard_input)
        layout.addWidget(QLabel("启动AI按键2:"))
        layout.addWidget(keyboard_input2)
        layout.addLayout(button_layout)

        self.keyboard_dialog = QDialog()
        self.keyboard_dialog.setWindowTitle("Set Keyboard")
        self.keyboard_dialog.setLayout(layout)
        self.keyboard_dialog.hide()

    def set_key_board_dialog(self):
        self.keyboard_dialog.show()

    def set_api_key(self):
        self.config.openai_api_key = self.api_dialog.findChild(QLineEdit).text()
        self.config.streaming = self.api_dialog.findChild(
            QCheckBox, "streaming"
        ).isChecked()
        self.config.play_sound = self.api_dialog.findChild(
            QCheckBox, "sound"
        ).isChecked()
        write_config(self.config)
        set_openai_key(self.config.openai_api_key)
        self.api_dialog.hide()

    def set_keyboard(self):
        self.config.generation_key1 = self.keyboard_dialog.findChild(
            QLineEdit, "generation_key1"
        ).text()
        self.config.generation_key2 = self.keyboard_dialog.findChild(
            QLineEdit, "generation_key2"
        ).text()
        write_config(self.config)
        self.start_keyboard_listener(self.config, self.keyboard_listener)
        self.keyboard_dialog.hide()

    def exit_dialog(self):
        if self.api_dialog.isVisible():
            self.api_dialog.hide()
        if self.keyboard_dialog.isVisible():
            self.keyboard_dialog.hide()

    def show_api_key_dialog(self):
        self.api_dialog.show()

    def play_notification_sound(self):
        if not self.config.play_sound:
            return
        if hasattr(sys, "_MEIPASS"):
            # Running from PyInstaller bundle
            asset_dir = os.path.join(sys._MEIPASS, "asset")
        else:
            asset_dir = "asset"

        playsound(os.path.join(asset_dir, "start.wav"))

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
        self.play_notification_sound()
        if self.config.streaming:
            self.toggle_text_edit(
                "", paste_result=False, stream=True, change_window_flag=False
            )
        else:
            self.toggle_text_edit(
                "", paste_result=True, stream=False, change_window_flag=False
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
            if not paste_result:
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

    def start_keyboard_listener(
        self,
        config: AIConfig,
        thread: typing.Optional[AIKeyboardListenerThread],
    ):
        if thread:
            thread.stop()
            thread.quit()
            thread.wait()

        new_thread = AIKeyboardListenerThread(self.stop_flag, config)
        new_thread.hotkey_signal.connect(self.generate_text)
        new_thread.menukey_signal.connect(self.toggle_window)
        new_thread.exit_signal.connect(self.exit_generation)
        new_thread.enter_signal.connect(self.enter_key_generate_text)

        new_thread.start()

        self.keyboard_listener = new_thread
