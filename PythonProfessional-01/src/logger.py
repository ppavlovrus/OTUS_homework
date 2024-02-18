import logging


def setup_logger():
    logging.basicConfig(filename='app.log',
                        filemode='w',
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger()
    return logger
