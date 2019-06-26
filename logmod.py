import logging, getpass

class Log():
    def __init__(self, S):
        FORMAT = S.logging['format']
        log_name = S.logging['name']
        if getpass.getuser() == 'root':
            logpath = '/root/' + log_name
        else:
            logpath = '/home/' + getpass.getuser() + '/' + log_name
        logging_level = getattr(logging, S.logging['level'])
        logging.basicConfig(format=FORMAT,filename=logpath,filemode='a', level=logging_level)
        self.info = logging.info
        self.debug = logging.debug
        self.warning = logging.warning