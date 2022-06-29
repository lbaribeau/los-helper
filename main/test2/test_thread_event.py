
# Run with python -i

import threading
from time import sleep

class MyThread(threading.Thread):
	def __init__(self, event):
		super().__init__()
		self.event=event
	def run(self):
		print("Thread started")
		self.event.wait()
		print("Thread done.")

class MyEvent(threading.Event):
	pass

event = MyEvent()
t1    = MyThread(event)
print(str(t1.event))
t1.start()
sleep(1)
event.set()

class ImplementNotify(MyThread):
	def notify(self, r, m):
		super().notify()

event=MyEvent()
t2=ImplementNotify(event)
t2.start()
sleep(1)
event.set()

class MyEventWithNotify(MyEvent):
	def notify(self, r, m):
		#super().notify() # Super doesn't have notify
		self.set()

event=MyEventWithNotify()
t3=MyThread(event)
t3.start()
sleep(1)
event.notify(1,2)



