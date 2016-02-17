import threading
import time
import Queue
import urllib
import urllib2
import urlparse
from    bs4 import  BeautifulSoup


class pool_master(threading.Thread):
    def __init__(self, thread_size = 0, task_size = None, url = '', domain = '', lock=None):
        threading.Thread.__init__(self)
        self.visited = set()
        self.pages = set()
        self.threads = []
        self.lock = lock
        
        self.wait_task = Queue.Queue()
        self.start_flag = False
        self.is_running = False
        self.finished_all = False
        self.dead_all = False
        
        self.thread_size = thread_size
        self.__init_threads__()

        self.timer = pool_master.timer(outter=self)
        
        #��ʼ���������
        self.task_size = task_size
        try:
            self.task_queue = Queue.Queue(task_size)
        except :
            print "���г�ʼ�����󣡣�"
        
        
        if url != '':
            pass
        else:
            self.pages.add(url)
        self.domain = domain
    class timer(threading.Thread):
        def __init__(self, outter = None):
            threading.Thread.__init__(self)
            self.outter = outter
            self.is_alive = True
            

        def run(self):
            i = 0
            while self.is_alive:
                if len(self.outter.visited) == len(self.outter.pages):
                    if self.outter.task_queue.qsize() == 0 and self.outter.wait_task.qsize() == 0:
                        i = i + 1
                        print "All Dead Count : " , i
                        time.sleep(3)
                    #self.outter.dead_all = True
                        if i == 3:
                            self.outter.dead_all = True
                        continue
                i = 0

        def stop(self):
            if self.is_alive != False:
                self.is_alive = False
                
                #time.sleep(5)
    class worker(threading.Thread):
        def __init__(self, group=None, target=None, name=None, args=(), 
                    kwargs=None, verbose=None, outter=None, lock=None, url=''):
            threading.Thread.__init__(self)
            self.outter = outter
            self.lock = lock
            self.start_flag = False
            self.finished_flag = False
            self.blocked_flag = False
            self.url = url
            self.pages = []
            self.name = name
            self.is_runnable = True
            
        def run(self):
            while self.is_runnable:
                #print self.name + ": I ' m working"
                if self.start_flag == True:
                    if self.url == '':
                        self.start_flag = False
                        continue
                    else:
                        
                        if self.url in self.outter.visited:
                            print "[^] " + self.name + " blocked!"
                            self.start_flag = False
                            if self.blocked_flag == True:
                                pass
                            else:
                                self.blocked_flag = True
                        else:
                            print self.name + "Working"
                            self.blocked_flag = False
                            self.pages = self.get_local_urls(url=self.url)
                            self.outter.visited.add(self.url)
                            self.start_flag = False
                            self.finished_flag = True
                            #self.start_flag = False
            
        #----------------------------------------------------------------------
        def get_local_urls(self,url=''):
            '''
            ��ȡͬһ�������µ�url
            '''
            if url == '':
                return []
            domain = self.outter.domain
            repeat_time = 0
            pages = set()
            newpage_flag = False
            data = ""
            #��ֹurl��ȡ��ס
            while True:
                try:
                    print self.name + "Ready to Open the web!"
                    time.sleep(1)
                    print self.name + "Opening the web", url
                    web = urllib2.urlopen(url=url,timeout=3)
                    print "Success to Open the web"
                    
                except:
                    print self.name + "Open Url Failed !!! Repeat"
                    time.sleep(1)
                    repeat_time = repeat_time+1
                    if repeat_time == 5:
                        return
                try:
                    data = web.read()
                    break
                except:
                    print "[!] Read Failed !"
            
            
            print self.name + "Reading the web ..."
            soup = BeautifulSoup(data)  
            print "..."
            tags = soup.findAll(name='a')
            for tag in tags:
                
                
                try:
                    ret = tag['href']
                except:
                    print "Maybe not the attr : href"
                    continue
                o = urlparse.urlparse(ret)
                """
                #Debug I/O
                for _ret in o:
                    if _ret == "":
                        pass
                    else:
                        print _ret
                """
                #�������·��url
                if o[0] is "" and o[1] is "":
                    print self.name + "Fix  Page: " + ret
                    url_obj = urlparse.urlparse(web.geturl())
                    ret = url_obj[0] + "://" + url_obj[1] + url_obj[2] + ret
                    #����url�ĸɾ�
                    ret = ret[:8] + ret[8:].replace('//','/')
                    #o = urlparse.urlparse(ret)
            
                    print "FixedPage: " + ret
                    
                    
                #Э�鴦��
                if 'http' not in o[0]:
                    print "Bad  Page��" + ret.encode('ascii')
                    continue
                
                #url�����Լ���
                if o[0] is "" and o[1] is not "":
                    print "Bad  Page: " + ret
                    continue
                
                #��������
                if self.outter.domain not in o[1]:
                    print "Bad  Page: " + ret
                    continue
                
                #��������
                newpage = ret
                newpage_flag = False
                self.lock.acquire()
                if newpage not in self.outter.pages:
                    print self.name + "Add New Page: " + newpage
                    #self.outter.pages.add(newpage)
                    self.pages.append(newpage)
                    newpage_flag = True
                else:
                    pass
                self.lock.release()
                
            return self.pages

        def stop(self):
            if self.is_runnable != False:
                self.is_runnable = False
    #��ʼ���߳�
    def __init_threads__(self):
        for i in range(self.thread_size):
            name = "V-%d " % i
            subthread = self.worker(outter = self,name=name, lock=lock)
            subthread.start()
            self.threads.append(subthread)
            
            print '[*] creating and starting thread %d total: %d' % (i,self.thread_size)
        print "[*] init threads completed"
        
    def __init_tasks__(self):
        pass
    
    def execute(self,tasks=[]):
        for task in tasks:
            self.wait_task.put(task)
        if self.is_running != True:
            self.start()



    #�̳߳���ѭ��
    def run(self):
        self.timer.is_alive = True
        self.timer.start()
        while True:
            self.is_running = True
            '''
            1.to dispatch tasks
            2.to protect the task_queue
            '''
            while self.start_flag:
                """
                print "Visited : Count = %d" % len(self.visited)
                print "Pages   : Count = %d" % len(self.pages)
                print "Wait_Queue size = %d" % self.wait_task.qsize()
                """
                k = 0
                for i in self.threads:
                    if i.start_flag == False:
                        #print i.name + " Dead!"
                        k = k + 1
                if k == len(self.threads):
                    #print "All Dead!"
                    if self.finished_all != True:
                        self.finished_all = True
                   
                if self.task_queue.empty() == False:
                    '''
                    ������Ҫע��ͬ��
                    �����ɷ�
                    '''                    
                    #url = self.task_queue.get()
                    for thread in self.threads:
                        if thread.start_flag == False:
                            if self.task_queue.empty() == True:
                                continue
                            self.lock.acquire()
                            tmp = self.task_queue.get()
                            self.pages.add(tmp)
                            self.lock.release()
                            thread.url = tmp
                            #self.visited.add(thread.url)
                            thread.start_flag = True
                else:
                    '''
                    ����ά��task_queue
                    '''
                    if self.wait_task.qsize() <= 0:
                        pass
                        
                            
                        """
                        for i in self.threads:
                            if i.blocked_flag != True:
                                self.finished_all = False
                                break
                            self.finished_all = True
                        if self.finished_all == True:
                            print "[!] Completed!!!"
                            for i in self.threads:
                                i.start_flag = False
                            return
                        """
                        
                        
                        
                    
                        """
                        if self.task_queue.empty() == True:
                            all_done = True
                            if self.visited >= self.pages:               
                                print "[!!!!]All Thread Closed!!!"
                                if all_done == True:                            
                                    print "[*] completed!"
                                    #return
                        """
                        #self.lock.release()
                    """
                    else:
                        while self.task_queue.full() == False:
                            if self.wait_task.qsize() <= 0:
                                break
                            self.lock.acquire()
                            url_tmp = self.wait_task.get()
                            self.task_queue.put(url_tmp)
                            self.lock.release()
                   """
                while self.task_queue.full() != True:
                    if self.wait_task.qsize() <= 0:
                        if self.task_queue.empty() == True:

                          pass       
                        break   
                    self.lock.acquire()
                    url_tmp = self.wait_task.get()
                    self.task_queue.put(url_tmp)
                    self.lock.release()
                '''
                �ռ����
                '''
                #self.finished_all = True
                self.lock.acquire()
                for thread in self.threads:
                    if thread.finished_flag == True:        
                        for page in thread.pages:
                            if page in self.pages:
                                continue
                            self.pages.add(page)
                            self.wait_task.put(page)
                self.lock.release()
                if self.dead_all == True:
                    break
                else:
                    pass
            if self.finished_all == True and self.dead_all == True:
                for i in self.pages:
                    print "Url : " + i
                break
        for thread in self.threads:
            thread.stop()
        self.timer.stop()
                                
                                       
                            



lock = threading.RLock()
#pool = pool_master(thread_size=5,task_size=5,url='http://villanch.top/',domain='121.42.165.233',lock=lock)
#pool = pool_master(thread_size=3, task_size=3, url="http://blog.helloqiu.pw/", domain='helloqiu.pw', lock=lock)
#pool = pool_master(thread_size=5, task_size = 5, url = "http://ilazycat.com/", domain="ilazycat.com", lock=lock)
pool = pool_master(thread_size=8, task_size = 10, url = 'http://freebuf.com/', domain='freebuf.com', lock=lock)
pool.start_flag = True
pool.execute(tasks=['http://freebuf.com/'])