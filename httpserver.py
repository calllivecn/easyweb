#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-07 15:38:26
# author calllivecn <c-all@qq.com>


import os
import ssl
import socket
from urllib import parse
from threading import Thread, Lock
from queue import Queue


class Request:
    pass

class Route:
    pass

class View:
    pass

class Handle:
    pass

class Server:

    def __init__(self, worker=os.cpu_count(), threads=10, queuemax=512):
        self.worker = worker
        self.threads = threads

        self.q = Queue(queuemax)

        self._pools = []
        for _ in range(self.threads):
            th = Thread(target=self.__proc, daemon=True)
            th.start()
            self._pools.append(th)
        

    def submit(self, func, *args, **kwargs):
        self.q.put((func, args, kwargs))
    
    def __proc(self):
        while True:
            func, args, kwargs = self.q.get()
            result = func(*args, **kwargs)


class Socket:

    def __init__(self, addr="::", port=8080):
        # start server
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
        sock.bind((addr, port))
        sock.listen(512)

        self.sock = sock
    
    def accept(self):
        client, addr, _, _ = self.sock.accept()
        return client, addr
