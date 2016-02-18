import threading
import Queue
import deamon_task_queue
import worker
import hashlib
try:
    import bsddb
except:
    print "Error For Importing bsddb"


class manager(threading.Thread):
    """The Main Manager"""
    def __init__(self,task_size = 10, thread_size = 5, domain = ''):
        threading.Thread.__init__(self)
        """Fields"""
        self.thread_size    = thread_size
        self.task_size      = task_size
        self.domain         = domain
        self.md5hash        = hashlib.md5()
             

        #Flag
        self.is_stopped     = True
        

        #BDB:
        self.all_sites  = None
        self.visited    = None
        self.__init_bdb__()

        

        """THREAD_TASK_QUEUE        To read the stored data and protect the task queue"""
        self.task_queue = Queue.Queue(task_size)
        self.deamon_task_queue = deamon_task_queue(master = manager)
        
        """THREAD_STORE_AND_DISPATCH_URL       2collect the results and store them"""
        self.deamon_manage_urls = deamon_manage_urls(master = manager)

        """THREAD_ANALYSIS(multi)   Analysis page"""
        self.workers = []
        self.__init_workers__()
        self.deamon_manage_worker = deamon_manage_worker(master = manager)

        """THREAD_DEAD_TIME         To check if all tasks have been done"""
        self.deanmon_all_dead = deanmon_all_dead(master = manager)

        """THREAD_LOG"""
        self.deamon_manage_logs = deamon_manage_logs(master = manager)
    def __init_dbd__(self):
        print "prepare to initial the bdb"
        """
>>> import bsddb
>>> db = bsddb.btopen('spam.db', 'c')
>>> for i in range(10): db['%d'%i] = '%d'% (i*i)
...
>>> db['3']
'9'
>>> db.keys()
['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
>>> db.first()
('0', '0')
>>> db.next()
('1', '1')
>>> db.last()
('9', '81')
>>> db.set_location('2')
('2', '4')
>>> db.previous()
('1', '1')
>>> for k, v in db.iteritems():
...     print k, v
0 0
1 1
2 4
3 9
4 16
5 25
6 36
7 49
8 64
9 81
>>> '8' in db
True
>>> db.sync()
0

        """
        try:
            self.all_sites  = bsddb.btopen(file = 'all_sites.db',   flag = 'c')
            self.visited    = bsddb.btopen(file = 'visited.db',     flag = 'c') 
            print "[*]Success init BDB"
        except:
            print "[!]Bad ! Can't create BDB!"
    
    def __init_workers__(self):
        """Create the workers!"""
        if self.workers == []:
            for i in range(self.thread_size):
                worker = worker(name = "V-%d" % i)
                worker.start()
                self.workers.append(worker)
            print "[*] Create %d workers!" % self.thread_size
        else:
            print "[!] Init the workers Failed !!!"   

    


    def run(self):
        print "Prepare to Run the Pool"
        if self.is_stopped == True:
            self.is_stopped = False
        else :
            pass


        while self.is_stopped == False:
            pass

    def check_url(self, url = ""):
        if url != "":
            self.md5hash.update(url)
            if self.visited.has_key(self.md5hash.hexdigest()) == 1:
                return 0
            elif self.all_sites.has_key(self.md5hash.hexdigest()) == 1:
                return 1
            else:
                return 2
    def not_in_visited(self, url = ""):
        flag = self.check_url(url)
        if flag == 0:
            return True
        else:
            return False
    def not_in_all_sites(self, url = ""):
        flag = self.check_url(url)
        if flag == 1:
            return True
        elif flag == 0:
            return True
        else:
            return False
    def add_all_sites(self, url = ""):
        if self.not_in_all_sites == True:
            self.md5hash.update(url)
            self.all_sites[self.md5hash.hexdigest()] = url 
            return 1
        else:
            print "[!] Existed URLs"
            return 0   

    def execute(self, tasks = []):
        if tasks != []:
            for task in tasks:
                if self.not_in_all_sites(task) == True:
                    flag = self.add_all_sites