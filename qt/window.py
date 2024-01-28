import datetime
import typing
from PyQt6 import QtGui
from PyQt6.QtWidgets import (
    QApplication,
    QPushBottom,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QMenuBar,
    QMenu,
    QDialog,
    QLabel,
    QHBoxLayout,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QRect
import time
from pynput.keyboard import Controller, Key
import os
from LLM.chatgpt import get_openai_response
import threading
import subprocess
import sys
from playsound import playsound
from config import AIConfig, write_config
from thread.keyword import AIKeyboardListenerThread
from logger_util import logger
from thread.mouse import MouseListenerThread


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


def get_selected_text(change_window_flag=False):
    copy(change_window_flag)
    logger.info("finish copy")
    try:
        output = subprocess.check_output(["pbpaste"]).decode("utf-8")
        return output
    except Exception as e:
        print(f"Command failed with error: {e}")
    return subprocess.check_output(["pbpaste"]).decode("utf-8")


class AIBottom:
    def __init__(self, config: AIConfig):
        self.app = QApplication([])
        self.config = config
        self.init_menu()
        self.active = False
        self.keyboard = Controller()
        self.keyboard_listener = None
        self.stop_flag = threading.Event()
        self.clicked_event = threading.Event()
        self.current_generation = threading.Event()
        self.mouse_listener = None
        self.buffer = []

    def init_menu(self):
        self.menu_bar = QMenuBar()

        file_menu = QMenu("File")
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.app.quit)
        file_menu.addAction(exit_action)

        self.menu_bar.addMenu(file_menu)

        api_menu = QMenu("Setting")
        set_api_action = QAction("Set AI", self.app)
        set_key_board_action = QAction("Set Hotkey", self.app)
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
        streaming_checkbox = QCheckBox("Streaming output")
        streaming_checkbox.setObjectName("streaming")
        streaming_checkbox.setChecked(self.config.streaming)
        sound_checkbox = QCheckBox("Play sound")
        sound_checkbox.setObjectName("sound")
        sound_checkbox.setChecked(self.config.play_sound)
        system_prompt_input = QLineEdit()
        system_prompt_input.setMinimumWidth(200)
        system_prompt_input.setText(self.config.system_prompt)
        system_prompt_input.setObjectName("system_prompt")
        save_bottom = QPushBottom("Save")
        save_bottom.clicked.connect(self.set_api_key)

        exit_bottom = QPushBottom("Exit")
        exit_bottom.clicked.connect(self.exit_dialog)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(save_bottom)
        bottom_layout.addWidget(exit_bottom)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Set OpenAI API Key"))
        layout.addWidget(api_key_input)
        layout.addWidget(streaming_checkbox)
        layout.addWidget(sound_checkbox)
        layout.addWidget(QLabel("System Prompt"))
        layout.addWidget(system_prompt_input)
        layout.addLayout(bottom_layout)

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
        save_bottom = QPushBottom("Save")
        save_bottom.clicked.connect(self.set_keyboard)

        exit_bottom = QPushBottom("Exit")
        exit_bottom.clicked.connect(self.exit_dialog)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(save_bottom)
        bottom_layout.addWidget(exit_bottom)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Hotkey1:"))
        layout.addWidget(keyboard_input)
        layout.addWidget(QLabel("Hotkey2:"))
        layout.addWidget(keyboard_input2)
        layout.addLayout(bottom_layout)

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
        self.config.system_prompt = self.api_dialog.findChild(
            QLineEdit, "system_prompt"
        ).text()
        write_config(self.config)
        self.api_dialog.hide()

    def set_keyboard(self):
        self.config.generation_key1 = self.keyboard_dialog.findChild(
            QLineEdit, "generation_key1"
        ).text()
        self.config.generation_key2 = self.keyboard_dialog.findChild(
            QLineEdit, "generation_key2"
        ).text()
        write_config(self.config)

        self.keyboard_dialog.hide()
        logger.info("finish set keyboard")

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

    def exit_generation(self):
        pass

    def generate_text(self):
        self.play_notification_sound()
        if self.config.streaming:
            self.toggle_text_edit(
                "",
                paste_result=False,
                stream=True,
            )
        else:
            self.toggle_text_edit(
                "",
                paste_result=True,
                stream=False,
            )

    def toggle_text_edit(
        self,
        prefix_prompt="",
        paste_result=True,
        stream=False,
    ):
        if not isinstance(prefix_prompt, str):
            prefix_prompt = ""
        logger.info(f"start toggle text edit in {datetime.datetime.now().isoformat()}")
        logger.info("Generating text")
        selected_text = get_selected_text()
        logger.info(f"Selected text: {selected_text}")
        result = ""
        if stream:
            gen = get_openai_response(
                f"{prefix_prompt}{selected_text}",
                key=self.config.openai_api_key,
                stream=True,
                prompt=self.config.system_prompt,
            )
            self.run_stream(gen)
        else:
            result = get_openai_response(
                f"{prefix_prompt}{selected_text}",
                key=self.config.openai_api_key,
                prompt=self.config.system_prompt,
            )

        if paste_result:
            process = subprocess.Popen(
                "pbcopy", universal_newlines=True, stdin=subprocess.PIPE
            )
            process.communicate(input=result)
            paste()

        # self.window.adjustSize()
        logger.info(f"end toggle text edit in {datetime.datetime.now().isoformat()}")

    def check_gen(self, response):
        if not response.choices:
            return None
        delta = response.choices[0].delta
        return delta.content

    def output_content(self, char):
        if char == "\n":
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            return
        keyboard.press(char)
        keyboard.release(char)

    def print_buffer(self):
        while self.buffer and not self.clicked_event.is_set():
            if self.stop_flag.is_set():
                break
            char = self.buffer.pop(0)
            self.output_content(char)
            time.sleep(0.01)

    def clean_event(self):
        self.stop_flag.clear()
        self.current_generation.clear()
        self.clicked_event.clear()
        self.buffer = []

    def run_stream(self, generator):
        self.clean_event()

        for response in generator:
            content = self.check_gen(response)
            if not content:
                continue
            if not self.current_generation.is_set():
                self.current_generation.set()
            if self.stop_flag.is_set():
                break
            for char in content:
                # if click event is set, then append char to buffer
                if self.clicked_event.is_set():
                    self.buffer.append(char)
                # if buffer is not empty, then print buffer
                elif self.buffer:
                    self.print_buffer()
                    self.buffer.append(char)
                # if buffer is empty, then print char
                else:
                    self.output_content(char)
            time.sleep(0.01)
        self.clean_event()

    def start_keyboard_listener(
        self,
        config: AIConfig,
    ):
        logger.info("start keyboard listener")
        new_thread = AIKeyboardListenerThread(
            self.stop_flag, self.current_generation, config
        )
        new_thread.hotkey_signal.connect(self.generate_text)

        new_thread.start()
        self.keyboard_listener = new_thread

    def start_mouse_listener(
        self,
    ):
        logger.info("start mouse listener")

        new_thread = MouseListenerThread(self.clicked_event, self.current_generation)

        new_thread.start()
        self.mouse_listener = new_thread
