import threading
import Queue
import hashlib
import os
try:
    import bsddb
except:
    print "Error For Importing bsddb"

import deamon_task_queue
import deamon_collect_urls
import deamon_all_dead
import deamon_logs
import worker


class manager(threading.Thread):
    """The Main Manager"""
    def __init_dbd__(self):
        print "prepare to initial the bdb"
        print "[#] Check if the db exist"
        if os.path.exists("all_sites.db"):
            os.remove('all_sites.db')

        if os.path.exists('visited.db'):
            os.remove('visited.db')
        print "[#] Cleared the db"
            
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
                _worker = worker.worker(name = "V-%d" % i, master = self)
                _worker.start()
                self.workers.append(_worker)
            print "[*] Create %d workers!" % self.thread_size
        else:
            print "[!] Init the workers Failed !!!"  

    def __init__(self,task_size = 10, thread_size = 5, domain = ''):
        threading.Thread.__init__(self)
        """Fields"""
        self.thread_size    = thread_size
        self.task_size      = task_size
        self.domain         = domain
        self.md5hash        = None


        self.task_buffer    = Queue.Queue()
             

        #Flag
        self.is_stopped     = True
        self.is_all_dead    = False
        

        #BDB:
        self.all_sites  = None
        self.visited    = None
        self.__init_dbd__()

        

        """THREAD_TASK_QUEUE        To read the stored data and protect the task queue"""
        self.task_queue = Queue.Queue(task_size)
        self.deamon_task_queue = deamon_task_queue.deamon_task_queue(master = self)
        
        """THREAD_STORE_AND_DISPATCH_URL       2collect the results and store them"""
        self.deamon_collect_urls = deamon_collect_urls.deamon_collect_urls(master = self)

        """THREAD_ANALYSIS(multi)   Analysis page"""
        self.workers = []
        self.__init_workers__()
        #self.deamon_manage_worker = deamon_manage_worker(master = manager)

        """THREAD_DEAD_TIME         To check if all tasks have been done"""
        self.deamon_all_dead = deamon_all_dead.deamon_all_dead(master = self)

        """THREAD_LOG"""
        self.deamon_logs = deamon_logs.deamon_logs(master = self,name = "deamon_logs")

    def run(self):
        print "Prepare to Run the Pool"
        if self.is_stopped == True:
            self.is_stopped = False
        else :
            pass
        self.deamon_collect_urls.start()
        self.deamon_task_queue.start()
        self.deamon_all_dead.start()
        self.deamon_logs.start()

        while self.is_stopped == False:
            for _worker in self.workers:
                if _worker.url == "":
                    if _worker.is_finished == False:
                        if self.task_queue.qsize() != 0:
                            _worker.url = self.task_queue.get()
                    else:
                        pass
                else:
                    pass
            if self.is_all_dead == True:
                break
            #print "Manager Working"

        self.deamon_all_dead.stop()
        print "[~] deamon_all_dead          stopped"
        self.deamon_collect_urls.stop()
        print "[~] deamon_collect_urls      stopped"
        self.deamon_logs.stop()
        print "[~] deamon_logs              stopped"
        self.deamon_task_queue.stop()
        print "[~] deamon_task_queue        stopped"
        for _worker in self.workers:
            _worker.stop()
            print "[~] worker", _worker.name , "stopped"
        
        print "[!] All done!"

        for k, v in self.all_sites.iteritems():
            print v



    def check_url(self, url = ""):
        if url != "":
            self.md5hash = hashlib.md5()
            self.md5hash.update(url)
            if self.visited.has_key(self.md5hash.hexdigest()) == 1:
                return 0
            elif self.visited.has_key(self.md5hash.hexdigest()) != 1 and self.all_sites.has_key(self.md5hash.hexdigest()) == 1:
                return 1
            else:
                return 2
    def not_in_visited(self, url = ""):
        flag = self.check_url(url)
        if flag == 0:
            return False
        else:
            return True
    def not_in_all_sites(self, url = ""):
        flag = self.check_url(url)
        if flag == 1:
            return False
        elif flag == 0:
            return False
        else:
            return True
    def add_all_sites(self, url = ""):
        if url == "":
            return 0
        if self.not_in_all_sites(url) == True:
            self.md5hash = hashlib.md5()
            self.md5hash.update(url)
            self.all_sites[self.md5hash.hexdigest()] = url 
            self.all_sites.sync()
            return 1
        else:
            print "[!] Existed URLs"
            return 0   
    def add_visited(self, url = ""):
        if url == "":
            return 0
        if self.not_in_visited(url) == True:
            self.md5hash = hashlib.md5()
            self.md5hash.update(url)
            self.visited[self.md5hash.hexdigest()] = url
            self.visited.sync()
            self.all_sites[self.md5hash.hexdigest()] = url
            self.all_sites.sync()
    def execute(self, tasks = []):
        if tasks != []:
            for task in tasks:
                self.add_all_sites(task)
                """For other part , we need to add the urls into the task_queue"""
                self.task_buffer.put(task)
            print "[^] Initial The Tasks"
        self.start()
        
