#!/usr/bin/env python3

import logging
import sys

from logging.handlers import TimedRotatingFileHandler

Formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(Formatter)
    return console_handler


def get_file_handler(logfile):
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(Formatter)

    return file_handler


def get_logger(logger_name, logfile="app.log"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(get_file_handler(logfile))
    logger.addHandler(get_console_handler())

    # no propagating the error
    logger.propagate = False

    return logger
