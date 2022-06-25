
import telnetlib
import socket
import time
import os
from threading import Thread

from misc_functions import magentaprint

class TelnetHandler(object):
    server_timeout = 299 

    def __init__(self):
        # proxy = '155.138.157.26:8080'

        # os.environ['http_proxy'] = proxy 
        # os.environ['HTTP_PROXY'] = proxy
        # os.environ['https_proxy'] = proxy
        # os.environ['HTTPS_PROXY'] = proxy

        connected = False
        while not connected:
            try:
                self.tn = telnetlib.Telnet('mud.landsofstone.org', 4801, 25)
                connected = True
            except socket.error as e:
                magentaprint("TelnetHandler connect timeout, retrying.")
                connected = False
                time.sleep(5)

        self.set_timer()
        self.thread = Thread(target=self.keep_connection_open)
        self.thread.daemon = True
        self.thread.start()
        self.echoing = False

    def set_timer(self):
        self.timer = time.time() + self.server_timeout

    def close(self):
        self.tn.close()

    def get_socket(self):
        return self.tn.get_socket()

    def read_some(self):
        try:
            # return self.tn.read_some()  # read_eager() would miss characters
            return self.tn.read_very_eager()  # This seems faster and also helps the tricky equipment parsing
        except socket.error as e:
            magentaprint("TelnetHandler read_some() error: " + str(e))
            # Server shutdown is errno 104
            return ''

    def write(self, command):
        if (self.echoing):
           magentaprint('"' + command + '"', False)
        
        self.set_timer()
        command += '\r'
        # magentaprint("\"" + command[:len(command)-1] + "\" ", end="")
        # magentaprint("Sending '" + command[:len(command)-1] + "'")
        try:
            self.tn.write(command.encode('ascii'))
        except socket.error:
            magentaprint("TelnetHandler write() error: " + str(socket.error))
            raise socket.error
        # After "### Shutting down now.", we get an exception on this write:
        # ConnectionAbortedError: [WinError 10053] An established connection was aborted 
        # by the software in your host machine

    def keep_connection_open(self):
        # The server times out every 5 minutes - I'd prefer it to be 10 minutes,
        # so I send a 'rest' command when we're about to time out.
        while True:
            while self.timer > time.time():
                time.sleep(max(0, self.timer - time.time()))
            self.tn.write('rest\r'.encode('ascii'))
            time.sleep(self.server_timeout)
            if self.timer < time.time():
                # If no command was sent in this time, we've timed out by now.
                # Sending a rest right after the timeout is actually a neat idea, 
                # it might cause the exception required to exit.
                return
