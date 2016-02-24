import manager
if __name__ != "__main__":
    __name__ = "__main__"


if __name__ == "__main__":

#    master = manager.manager(domain = "ilazycat.com")
#    master.execute(tasks = ['http://ilazycat.com/'])
    master = manager.manager(thread_size = 6, domain = "helloqiu")
    master.execute(tasks = ['http://blog.helloqiu.pw'])

