import threading
class worker(threading.Thread):
    """This class works as a slave to collect the url"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_stopped = True
    def run(self):
        if self.is_stopped == True:
            self.is_stopped = False

        while self.is_stopped == False:
            pass
    def stop(self):
        if self.is_stopped == False:
            self.is_stopped = True

