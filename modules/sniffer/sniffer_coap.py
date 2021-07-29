from termcolor import colored, cprint
from module import Module

import threading
import time

from printib import print_error, print_info, print_ok
from scapy.all import *
from scapy.contrib.coap import CoAP

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "CoAP sniffer",
                       "Description": "Sniffs CoAP protocol",
                       "Author": "Marcos Rivera Martínez @marcos_rm_98"}

        # -----------name-----default_value--description--required?
        options = {
            "interface": ["lo", "Interface for sniffing", True],
            "filter": ["port 5683", "BPF filter", False],
            "mode": [0, "Mode 0 -> Show hex packets. Mode 1 -> Show raw packets", False],
            "count": [None, "Number of packets to sniff", False],
            "toFile": [None, "Save the results in a file and execute it in background", False],
        }

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def go(interface, bpffilter, count, toFile):
            def write(pkt):
                wrpcap(toFile, pkt, append=True)

            print_ok("Start sniffing")
            print_ok("Results save in {}".format(toFile))
            print("")
            sniff(iface=interface, prn=write, filter=bpffilter, count=count)

        def raw_sniff_callback(pkt):
            hexdump(pkt) 
            print("") 
            print("")    

        def sniff_callback(pkt):
            pkt.show()
            print("")
            print("")

        interface = self.options.get("interface")[0]
        bpffilter = self.options.get("filter")[0]
        mode = int(self.options.get("mode")[0])
        count = self.options.get("count")[0]
        toFile = self.options.get("toFile")[0]
        error = False

        if count is None:
            count = 0

        if mode is None:
            mode = 0

        if toFile is not None and toFile.lower() != "none":
            toFile = os.path.abspath(toFile)
            if not os.path.isdir(toFile):
                error = True
                print_error("The dir path is not correct")

            if (not error):
                toFile += "/sniff_mqtt.pcap"
                thread1 = threading.Thread(target=go, args=[interface, bpffilter, count, toFile])
                thread1.start()
                super(CustomModule, self).run(t=thread1)
        else:
            if mode == 0:
                print_ok("Starting sniffing... Use Ctr + C to stop")
                sniff(iface=interface, prn=raw_sniff_callback, filter=bpffilter, count=count) 
                print_ok("Finishing sniffing...") 

            if mode == 1:
                print_ok("Starting sniffing... Use Ctr + C to stop")
                sniff(iface=interface, prn=sniff_callback, filter=bpffilter, count=count) 
                print_ok("Finishing sniffing...") 
