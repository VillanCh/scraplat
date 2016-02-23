import threading
import manager
import time
import urllib
import urllib2
import urlparse
import hashlib
from bs4 import BeautifulSoup

class worker(threading.Thread):
    """This class works as a slave to collect the url"""
    def __init__(self, master = None, name = None, handler = None):
        threading.Thread.__init__(self, name = name)
        self.is_stopped = True
        #self.name       = name
        self.master     = master
        self.pages      = set()
        self.url        = ""
        self.md5hash    = hashlib.md5()
        self.soup       = None
        self.webdata    = ""
        
        #handler interface
        self.handler    = handler


        #Status Flag
        self.is_finished = False
        self.is_working = False

    def run(self):
        if self.is_stopped == True:
            self.is_stopped = False

        while self.is_stopped == False:
            if self.is_finished == False:
                if self.url == "":
                    if self.is_working == True:
                        self.is_working = False
                        continue
                if self.url != "":
                    if self.is_working == False:
                        self.is_working = True
                    else:
                        pass
                    self.md5hash.update(self.url)
                    if self.master.not_in_visited(self.url) == True:
                        self.master.add_visited(self.url)
                        results = self.analyze(self.url)
                        if results == 1:
                            self.is_working = False
                            self.is_finished = True
                            
                        else:
                            pass
                            #print "[^] " + self.name + " Empty URLs in ", self.url
                        self.url = ""
                        
                    else:
                        print "[^] " + self.name + " Repeated URLs : ", self.url
                else:
                    #print "[^] " + self.name + " Empty URLs : ", self.url
                    pass
                
                if self.is_working == True:
                    self.is_working = False
                else:
                    pass
            else:
                pass

    def stop(self):
        if self.is_stopped == False:
            self.is_stopped = True

    def get_webdata(self, url = '', headers = {}, use_cookie = False):
        if url == '':
            return 0
        web         =   None
        #data        =   ""
        repeat_time =   0
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
                repeat_time = repeat_time + 1
                if repeat_time == 5:
                    return 0
            try:
                self.webdata = web.read()
                break
            except:
                print "[!] Read Failed !"
    def dig_urls(self,url=''):

        #if url == '':
        #    return []
        domain = self.master.domain
        #repeat_time = 0
        pages = set()
        newpage_flag = False
        #data = ""
        """
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
        self.soup = BeautifulSoup(data)  
        """
        print "..."
        tags = self.soup.findAll(name='a')
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
            # check the relative path 
            if o[0] is "" and o[1] is "":
                print self.name + "Fix  Page: " + ret
                #???
                url_obj = urlparse.urlparse(url)
                ret = url_obj[0] + "://" + url_obj[1] + url_obj[2] + ret

                ret = ret[:8] + ret[8:].replace('//','/')
                #o = urlparse.urlparse(ret)
        
                print "FixedPage: " + ret
                
                   
            if 'http' not in o[0]:
                print self.name + " Bad  Page" + ret.encode('ascii')
                continue

            if o[0] is "" and o[1] is not "":
                print self.name + " Bad  Page: " + ret
                continue

            if self.master.domain not in o[1]:
                print self.name + " Bad  Page: " + ret
                continue
            
            newpage = ret
            if newpage_flag != False:
                newpage_flag = False
            """Here to use bdb to check the visited url"""
            if self.master.not_in_all_sites(newpage) == True:
                if newpage not in self.pages:
                    print "[^] " + self.name + " Add New Page : " + newpage
                    self.pages.add(newpage)
                if newpage_flag != True:
                    newpage_flag = True
            else:
                print "[^] " + self.name + " Existed Page : " + newpage
        if newpage_flag == True:
            return 1
        else:
            return 0
    def get_soup(self, url = ''):
        """
        if url == '':
            return 0
        web         =   None
        data        =   ""
        repeat_time =   0
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
                repeat_time = repeat_time + 1
                if repeat_time == 5:
                    return 0
            try:
                data = web.read()
                break
            except:
                print "[!] Read Failed !"
        """
        
        print self.name + "Reading the web ..."
        self.soup = BeautifulSoup(self.webdata)  
        print self.name + "Success Read the Web ..."          
    def analyze(self, url):
        flag = self.get_webdata(url)
        if flag == 0:
            return 0
        #############################################
        #   if you dont want to use BeautifulSoup   #
        #   you can change from get_soup            #
        #############################################
        flag = self.get_soup(url)
        if flag == 0:
            return 0

        flag = self.dig_urls(url)
        if flag == 0:
            return 0

        return 1
    def reset(self):
        self.pages      = set()
        self.url        = ""
        self.soup       = None
        self.webdata    = ""

