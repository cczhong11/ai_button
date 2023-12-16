import sys

from config import read_config

from qt.window import AIBubble

import time


def main():
    config = read_config()

    bubble = AIBubble(config)
    app = bubble.app

    bubble.start_keyboard_listener(config, None)
    time.sleep(1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
