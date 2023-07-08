from command.Ask import Ask

class Talk(Ask):
    command = 'talk'

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)