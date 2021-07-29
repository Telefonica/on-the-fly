from termcolor import colored, cprint
from module import Module
from printib import * 
import os
import socket
import time
import threading


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "TCP Port Forwarding",
                       "Description": "Create a port forwarding rule ",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"local_host": ["0.0.0.0", "Interface - A. Local host to listen", True],
                   "local_port": [None, "Listen Port on interface A", True],
                   "remote_host": [None, "Interface - B (Remote). Remote host to connect", True],
                   "remote_port": [None, "Remote port to connect", True],
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

            #Create server socket(interface - A or Point - A)
            sockserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockserver.bind((self.options["local_host"][0],int(self.options["local_port"][0])))
            sockserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sockserver.listen(10)
            sockserver.settimeout(1)
            if verbose:
                print_info("Server socket created")

            #list threads
            threads = []
            t = threading.currentThread()
            while getattr(t, "do_run", True):

                #Create client socket(connect to Interface - B or Point - B)
                sockclient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

                try:
                    #Waiting for first connection (on Interface - A Extreme)
                    sockA = sockserver.accept() #tupla -> socket,address [0][1]
                    sockAsocket = sockA[0]
                    sockB = sockclient
                    sockB.connect((self.options["remote_host"][0],int(self.options["remote_port"][0])))
                    if verbose:
                        print_info("Client socket created")
                    sockBsocket = sockB

                    thread1 = threading.Thread(target=go, args=(sockAsocket,sockBsocket,options))
                    thread1.start()
                    thread2 = threading.Thread(target=go, args=(sockBsocket,sockAsocket,))
                    thread2.start()
                    threads.append(thread1)
                    threads.append(thread2)

                except:
                    pass

            #destroy threads
            for t in threads:
                t.do_run = False

            print_info("\nDeleted Port-Forward rule")
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
