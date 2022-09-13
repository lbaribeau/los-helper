
from reactions.alerter import Alerter
from reactions.health_monitor import HealthMonitor

class Analyser(object):
    # This is a layer between character/prompt/mobs/info (bottom reaction layer) and los-helper
    def __init__(self, mud_reader_handler, prompt, info):
        self.alerter = Alerter(prompt, info)
        mud_reader_handler.add_subscriber(self.alerter)
        self.health_monitor = HealthMonitor(prompt, info)
        mud_reader_handler.add_subscriber(self.health_monitor)
