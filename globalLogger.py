import logging
import datetime
global logger
logger = logging.getLogger('test')
def _init():
    print("INIT logger")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    logger = logging.getLogger('test')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s: %(message)s')
    file_handler = logging.FileHandler(f'{today}-user.log')
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
