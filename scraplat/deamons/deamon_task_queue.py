class deamon_task_queue(threading.Thread):
    def __init__(self, master = None, name = "deamon_task_queue"):
        threading.Thread.__init__(self)
        self.master = master
        self.is_stopped = True
    def run(self):
        self.is_stopped = False
        while self.is_stopped == False:
            pass
        
    def stop(self):
        if self.is_stopped == False:
            self.is_stopped = True


