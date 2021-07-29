from termcolor import colored, cprint
from module import Module
from printib import * 
import os
import socket
import time
import threading
from scapy.all import * 


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "Proxy SOCKS4",
                       "Description": "Proxy SOCKS4",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"local_host": ["0.0.0.0", "Interface. Local host to listen", True],
                   "local_port": ["1080", "Listen Port", True],
                   "verbose": ["False", "Verbose", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def control(t2):
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                time.sleep(1)
            t2.do_run = False
            #e.set()

        def sockets(options):
            
            verbose = options["verbose"][0] in ["True","true"]

            #Create server socket
            sockserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockserver.bind((self.options["local_host"][0],int(self.options["local_port"][0])))
            sockserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockserver.listen(10)
            sockserver.settimeout(1)
            if verbose:
                print_info("Server SOCKS4 created")

            #list threads
            threads = []
            t = threading.currentThread()
            while getattr(t, "do_run", True):

                try:
                    #Waiting for first connection (on Interface - A Extreme)
                    sockA = sockserver.accept() #tupla -> socket,address [0][1]
                    sockAsocket = sockA[0]
                    
                    #SOCKS4
                    # VERSION + COMMAND + DSTPORT + DSTIP
                    #  1byte     1byte     2byte    4byte

                    version = ord(sockAsocket.recv(1))
                    #print("version: " + str(version))
                    if not version == 4:
                        raise Exception
                    command = ord(sockAsocket.recv(1))
                    #print("command: " + str(command))
                    if not command == 1:
                        raise Exception
                    dstportA = sockAsocket.recv(1)
                    dstportB = sockAsocket.recv(1)
                    port = 256 * ord(dstportA) + ord(dstportB)
                    #print("port:" + str(port))
                    ipA = sockAsocket.recv(1)
                    ipB = sockAsocket.recv(1)
                    ipC = sockAsocket.recv(1)
                    ipD = sockAsocket.recv(1)
                    ip = str(ord(ipA)) + "." + str(ord(ipB)) + "." + str(ord(ipC)) + "." + str(ord(ipD))
                    #print("ip: " + str(ip))
                    userid = ord(sockAsocket.recv(1))

                    #Reply to client SOCKS
                    # VERSION + COMMAND + DSTPORT + DSTIP
                    a = dstportA + dstportB + ipA + ipB + ipC + ipD
                    b = bytes(chr(0).encode('utf-8')) + bytes(chr(90).encode('utf-8'))
                    reply =  b + a
                    sockAsocket.sendall(reply)

                    sockclient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sockclient.connect((ip,port))
                    sockB = sockclient
                    if verbose:
                        print_info("Client socket created")

                    thread1 = threading.Thread(target=go, args=(sockAsocket,sockB,options))
                    thread1.start()
                    thread2 = threading.Thread(target=go, args=(sockB,sockAsocket,))
                    thread2.start()
                    threads.append(thread1)
                    threads.append(thread2)

                except:
                    pass

            #destroy threads
            for t in threads:
                t.do_run = False

            print_info("\nClosed Proxy SOCKS4")
            try:
                sockserver.shutdown(socket.SHUT_RDWR)
                sockserver.close()
                sockclient.shutdown(socket.SHUT_RDWR)
                sockclient.close()
            except:
                pass
            

        def go(sockA,sockB,options=None):
            verbose = False
            if options:
                verbose = options["verbose"][0] in ["True","true"]
                if verbose:
                    src = sockA.getsockname()[0]
                    dst = sockB.getsockname()[0]

            t = threading.currentThread()
            while getattr(t,"do_run", True):
                try:
                    buff = sockA.recv(2048)
                    if len(buff) != 0:
                        if verbose:
                            print_info("%s --> %s" % (src,dst))
                        sockB.send(buff)
                except socket.error:
                    t.do_run = False

        
        #Create threads sockA -> sockB and sockA <- sockB 

        #e = threading.Event()

        thread2 = threading.Thread(target=sockets, args=(self.options,))
        thread2.start()

        thread1 = threading.Thread(target=control, args=(thread2,))
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
