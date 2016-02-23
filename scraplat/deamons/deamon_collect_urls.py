import threading
import manager

class deamon_collect_urls(threading.Thread):
    """This Class is For Collect The Results From Other Worker"""
    def __init__(self, master = None, name = "deamon_collect_urls"):
        threading.Thread.__init__(self)
        self.name = name
        self.is_stopped = True
        self.master = master

    def run(self):
        if self.is_stopped != False:
            self.is_stopped = False

        while self.is_stopped == False:
            for _worker in self.master.workers:
                if _worker.is_finished == True:
                    for page in _worker.pages:
                        if self.master.not_in_all_sites(page) == True:
                            self.master.add_all_sites(page)
                            self.master.task_buffer.put(page)
                        else:
                            pass
                    _worker.reset()
                    _worker.is_finished = False
                else:
                    pass


    def stop(self):
        if self.is_stopped != True:
            self.is_stopped = True
        else:
            pass
