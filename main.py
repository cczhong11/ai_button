import sys

from config import read_config

from qt.window import AIBottom

import time


def main():
    config = read_config()

    bubble = AIBottom(config)
    app = bubble.app

    bubble.start_keyboard_listener(config)
    time.sleep(0.1)
    bubble.start_mouse_listener()
    time.sleep(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
