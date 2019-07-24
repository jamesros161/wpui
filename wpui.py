#!/usr/bin/python3
"""Main application module"""
# -*- coding: utf-8 -*-
import os
import sys
import tempfile

from datetime import datetime
from application import App
from settings import Settings
from widgets import CustomWidgets
from logmod import Log
W = CustomWidgets()
L = Log()
S = Settings()
PYTHONIOENCODING = "utf-8"
sys.excepthook = L.handle_exception
L.info("\n****\nApplication Started at %s \n\n****\n",
       datetime.strftime(
           datetime.now(),
           "%Y-%m-%d %H:%M:%S.%f"))


def main():
    """Starts main loop"""
    S.app['home_dir'] = os.path.expanduser("~")
    tempfile.tempdir = S.app['home_dir']
    temporary_directory = tempfile.TemporaryDirectory()
    S.app['temp_dir'] = temporary_directory
    L.debug('temp_dir: %s', S.app['temp_dir'])

    app = App(S)
    L.debug('AppInstance: %s', app)
    app.views.activate(None, {"view": "Installs"})
    app.loop.run()

    L.info(
        "\n****\nApplication Ended Normally at %s \n\n****\n",
        datetime.strftime(
            datetime.now(),
            "%Y-%m-%d %H:%M:%S.%f"))


if __name__ == '__main__':
    main()
