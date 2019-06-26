#!/usr/bin/python2.7
from settings import Settings
S = Settings()
from logmod import Log
L = Log(S)
from widgets import CustomWidgets
W = CustomWidgets(S,L)
from Application import App
def main():
    L.debug('Test Logging')
    app = App(S,L,W)
    app.views.activate('home')
    app.loop.run()

if __name__ == '__main__':
    main()
