import sys
import subprocess
from thread.keyword import AIKeyboardListenerThread
from qt.window import AIBubble
from thread.mouse import MouseListenerThread
import time


def main():
    bubble = AIBubble()
    app = bubble.app
    mouse_listener = MouseListenerThread()

    mouse_listener.mouse_click_signal.connect(bubble.move_button)
    mouse_listener.start()
    time.sleep(1)  # Wait for the mouse listener to start
    keyboard_listener = AIKeyboardListenerThread()
    keyboard_listener.hotkey_signal.connect(bubble.generate_text)
    keyboard_listener.menukey_signal.connect(bubble.toggle_window)
    keyboard_listener.exit_signal.connect(bubble.exit_generation)
    keyboard_listener.start()

    time.sleep(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
