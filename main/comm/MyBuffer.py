
# Buffer used by MudListener and MudReader.
# MudListener writes to it and MudReader reads from it.
# MudListener appends and MudReader removes data the beginning.

import threading

class MyBuffer(threading.Event):
    def __init__(self, size_in=10000):
        super().__init__()
        self.set() # Default is to not have to wait (.clear() sets up waiting)
        self.buffer = ""
        # self.access_flag = False
        self.size = size_in

