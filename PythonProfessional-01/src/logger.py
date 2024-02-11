import logging


def logger_creator(log_filename):
    # Create and configure logger
    logging.basicConfig(filename=log_filename,
                        format='%(asctime)s %(message)s',
                        filemode='w')

    # Creating an object
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger
