from pynput import mouse
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from logger_util import logger


class MouseListenerThread(QThread):
    # Add class docstring here
    def __init__(self, clicked_event, current_generation) -> None:
        super(MouseListenerThread, self).__init__()
        self.clicked_event = clicked_event
        self.current_generation = current_generation

    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if not self.current_generation.is_set():
            return
        if not pressed:  # only emit when mouse is released
            if self.clicked_event.is_set():
                self.clicked_event.clear()
                logger.info(f"Mouse clicked and cleaned thread event")
            else:
                self.clicked_event.set()
                logger.info(f"Mouse clicked and set thread event")
