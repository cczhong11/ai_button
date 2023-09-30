import sys

from LLM.chatgpt import set_openai_key
from config import read_config

from qt.window import AIBubble
from thread.mouse import MouseListenerThread
import time


def main():
    config = read_config()
    if config.openai_api_key is not None:
        set_openai_key(config.openai_api_key)
    bubble = AIBubble(config)
    app = bubble.app
    mouse_listener = MouseListenerThread()

    mouse_listener.mouse_click_signal.connect(bubble.move_button)
    mouse_listener.start()
    time.sleep(1)  # Wait for the mouse listener to start
    bubble.start_keyboard_listener(config, None)
    time.sleep(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
