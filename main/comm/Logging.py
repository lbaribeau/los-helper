
from datetime import datetime

from db.Log import Log
from comm.ConsoleHandler import newConsoleHandler
from db.Database import *

class Logging(object):
    debugMode = True
    verboseMode = True
    startTime = datetime.now()

    def __init__(self):
        VERSION = "2"
        #databaseFile = "maplos.db"

    def print(text, is_debug_command=True, log_output=False, show_hidden=False):
        if show_hidden:
            text = repr(text)  # escape all characters in string

        if self.debugMode or not is_debug_command:
            do_magentaprint(text)

        if log_output:
            log = Log()
            log.data = text
            log.save()

    def do_magentaprint(text):
        newConsoleHandler().magenta()
        # output = str(get_timestamp() + "| <" + str(text) + ">")
        output = str(self.get_timestamp() + "   | " + str(text))  

        print(output)
        newConsoleHandler().white()

    def get_timestamp():
        curtime = datetime.now().time().strftime("%H:%M:%S.%f")
        return curtime[:len(curtime)-5]
