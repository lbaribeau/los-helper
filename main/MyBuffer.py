# Buffer used by MudListener and MudReader.
# MudListener writes to it and MudReader reads from it.
# MudListener appends and MudReader removes data the beginning.

class MyBuffer(object):
 
    def __init__(self, size_in=10000):
        self.buffer = ""
        self.access_flag = False
        self.size = size_in
