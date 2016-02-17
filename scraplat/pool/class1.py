import threading
import Queue
import deamon_task_queue

class manager(threading.Thread):
    """The Main Manager"""
    def __init__(self,task_size = 10):
        threading.Thread.__init__(self)
        """Fields"""
        

        """THREAD_TASK_QUEUE        To read the stored data and protect the task queue"""
        self.task_queue = Queue.Queue(task_size)
        self.deamon_task_queue = deamon_task_queue(master = manager)
        
        """THREAD_STORE_AND_DISPATCH_URL       2collect the results and store them"""
        self.deamon_manage_urls = deamon_manage_urls(master = manager)

        """THREAD_ANALYSIS(multi)   Analysis page"""
        self.workers = []
        self.deamon_manage_worker = deamon_manage_worker(master = manager)

        """THREAD_DEAD_TIME         To check if all tasks have been done"""
        self.deanmon_all_dead = deanmon_all_dead(master = manager)

        """THREAD_LOG"""
        self.deamon_manage_logs = deamon_manage_logs(master = manager)

            