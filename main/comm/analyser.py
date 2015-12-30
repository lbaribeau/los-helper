
from reactions.alerter import Alerter
from reactions.health_monitor import HealthMonitor

class Analyser(object):
    # This is a layer between character/prompt/mobs/info (bottom reaction layer) and los-helper
    def __init__(self, mud_reader_handler, character):
        self.alerter = Alerter(character)
        self.health_monitor = HealthMonitor(character)
        mud_reader_handler.add_subscriber(self.alerter)
        mud_reader_handler.add_subscriber(self.health_monitor)
