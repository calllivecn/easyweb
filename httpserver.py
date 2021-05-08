#!/usr/bin/env python3
# coding=utf-8
# date 2021-05-07 15:38:26
# author calllivecn <c-all@qq.com>


import os
import ssl
import socket
from urllib import parse
from queue import Queue
from threading import Thread, Lock
from multiprocessing import Process


class Request:
    pass

class Route:
    pass

class View:
    pass

class Handle:
    """
    每个请求的总的请求入口:
    1. 每个连接进来，首先走这里
    2. 路由 url 
    3. 维护数据库的连接?
    4. 中间件的列表调用，与维护。
    """

    def __init__(self, sock):
        self.sock = sock

    def __call__(self):
        pass


class ThreadPool:
    """
    线程池处理
    """
    def __init__(self, threads=10, queuemax=512, addr="::", port=8080, listen=512, certfile=None, keyfile=None):
        # start server
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
        sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)

        # ssl
        if certfile and keyfile:
            sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            sslcontext |= ssl.OP_NO_TLSv1
            sslcontext |= ssl.OP_NO_TLSv1_1
            sslcontext.load_cert_chain(certfile=certfile, keyfile=keyfile)

            sock = sslcontext.wrap_socket(sock, server_side=True)

        sock.bind((addr, port))
        sock.listen(listen)

        self.sock = sock

        # thread pool
        self.threads = threads

        self.q = Queue(queuemax)

        self._pools = []
        for _ in range(self.threads):
            th = Thread(target=self.__proc, daemon=True)
            th.start()
            self._pools.append(th)
        
    def accept(self):
        sock_info = self.sock.accept()
        client, addr = sock_info[0], sock_info[1]
        return client, addr

    def submit(self, func, *args, **kwargs):
        self.q.put((func, args, kwargs))
    
    def __proc(self):
        while True:
            func, args, kwargs = self.q.get()

            if func == b"quit":
                break

            result = func(*args, **kwargs)
    
    def close(self):
        for _ in range(len(self._pools)):
            self.q.put((b"quit", None, None))

        for th in self._pools:
            th.join()


class Server:

    def __init__(self):
        self.CPUs = os.cpu_count()

        self.procs = []
        for i in range(self.CPUs):
            proc = Process(target=self.process, daemon=True)
            proc.start()
            self.procs.append(proc)


    def process(self):
        threadpool = ThreadPool()
        threadpool.submit()


    def close(self):
        for proc in self.procs:
            proc.terminate()