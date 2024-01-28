import logging
import os

# log to file
USER_HOME = os.path.expanduser("~") + "/.ai_bottom"
logging.basicConfig(
    filename=os.path.join(USER_HOME, "ai_bottom.log"),
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger(__name__)
