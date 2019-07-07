#!/usr/bin/python
"""Main application module"""
# -*- coding: utf-8 -*-
import sys
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
    app = App()
    app.views.activate(app, 'Home')
    app.loop.run()
    L.info(
        "\n****\nApplication Ended Normally at %s \n\n****\n",
        datetime.strftime(
            datetime.now(),
            "%Y-%m-%d %H:%M:%S.%f"))


if __name__ == '__main__':
    main()
