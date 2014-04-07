
class MyBuffer:
    
    def __init__(self, size_in=10000):
        self.buffer = ""
        self.access_flag = False
        self.size = size_in
    