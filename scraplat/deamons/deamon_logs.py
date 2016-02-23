import threading 
import manager
import time

class deamon_logs(threading.Thread):
    """This Class is to Output the Logs from Manager"""
    def __init__(self, name = None, master = None):
        threading.Thread.__init__(self, name = name)
        self.master         = master
        self.is_stopped     = True

        self.tmp_logs       = "" 
        self.debug_tasks    = True
    
    def run(self):
        if self.is_stopped == True:
            self.is_stopped = False
        else :
            pass

        while self.is_stopped == False:
            time.sleep(2)
            self.print_task_status()

    def print_task_status(self):
        print 
        print " Task    Status:"
        print " Task Buffer Count:", self.master.task_buffer.qsize()
        print " Task Queue  Count:", self.master.task_queue.qsize()
        print " Workers Status:"
        for thread in self.master.workers:
            print " " + thread.name + ":" 
            print " IS_finished : ",    thread.is_finished
            print " IS_stopped  : ",    thread.is_stopped
            print " IS_working  : ",    thread.is_working

    def stop(self):
        if self.is_stopped == False:
            self.is_stopped = True

