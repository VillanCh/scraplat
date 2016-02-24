import manager
if __name__ != "__main__":
    __name__ = "__main__"


if __name__ == "__main__":

#    master = manager.manager(domain = "ilazycat.com")
#    master.execute(tasks = ['http://ilazycat.com/'])

    master = manager.manager(thread_size = 10, domain = "121.")
    master.execute(tasks = ['http://villanch.top/'])

