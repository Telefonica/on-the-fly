from termcolor import colored, cprint
from module import Module

from scapy.all import *
from printib import * 
import threading
import os
import time

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "sniff",
                       "Description": "Custom sniffer",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["eth0", "Interface for sniffing", True],
                   "filter": [None, "Filter for sniffing (BPF mode)", False],
                   "savePcap": ["True", "Save to PCAP File", True],
                   "filename": ["on_the_fly.pcap", "Filename PCAP", False],
                   "verbose": ["False", "Verbose or display info connections (IP and Ports)", True],
                   "showPayload": ["False", "Show payload connections TCP/UDP", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def control(e,t2):
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                time.sleep(1)
            t2.do_run = False
            e.set()

        def go(e,options):

            verbose = options["verbose"][0] in ["True","true"]
            savePcap = options["savePcap"][0] in ["True","true"]
            filename = options["filename"][0]
            filterSniff = options["filter"][0]
            if savePcap:
                print_info("Saving PCAP File at: "+ str(os.getcwd()))
                myPcap = PcapWriter(filename, append=True,sync=True)
                
            def packet_callback(packet):
                if savePcap:
                    myPcap.write(packet)
                
                if options["verbose"][0] in ["true","True"]:
                    if packet.haslayer(IP):
                        print_info("\n IP src: %s ---> IP dst: %s" % (packet[IP].src, packet[IP].dst))
                        if packet.haslayer(TCP):
                            print_info("\n Port src: %s Port dst: %s" % (packet[TCP].sport, packet[TCP].dport))
                            if options["showPayload"][0] in ["true","True"]:
                                print_info("\n TCP Payload: %s \n\n" % packet[TCP].payload)
                        if packet.haslayer(UDP):
                            print_info("\n Port src: %s Port dst: %s" % (packet[UDP].sport, packet[UDP].dport))
                            if options["showPayload"][0] in ["true","True"]:
                                print_info("\n UDP Payload: %s \n\n" % packet[UDP].payload)
                        if not packet.haslayer(TCP) and not packet.haslayer(UDP):
                            if options["showPayload"][0] in ["true","True"]:
                                print_info("\n IP Payload: %s \n\n" % packet[IP].payload)

            t = threading.currentThread()
            while getattr(t, "do_run", True):
                if filterSniff:
                    sniff(filter=filterSniff, prn=packet_callback, store=0, stop_filter=lambda p: e.is_set())
                else:
                    sniff(prn=packet_callback, store=0, stop_filter=lambda p: e.is_set())             
 
        e = threading.Event()
        thread2 = threading.Thread(target=go, args=(e,self.options,))
        thread2.start()        
        thread1 = threading.Thread(target=control,args=(e,thread2,))
        thread1.start()
       
        super(CustomModule, self).run(t=thread1)
