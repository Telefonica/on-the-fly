from termcolor import colored, cprint
from module import Module

from scapy.all import *
import threading
from printib import * 
from subprocess import Popen, PIPE
from netaddr import IPNetwork
from concurrent.futures import ThreadPoolExecutor


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "ARP Scan - Discovery machines",
                       "Description": "ARP Scan for discovering machines",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["eth0", "Interface for sniffing", True],
                    "threads": ["1", "Threads for execute", True],
                    "cidr": [None, "Network/CIDR for scanning", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def arp_request(ipdst,myipaddress,myhwaddress,interface):
            if not ipdst == myipaddress and not str(ipdst) in "192.168.0.0" and not str(ipdst) in "192.168.0.255":
                arp_request_packet=Ether(dst=ETHER_BROADCAST)/ARP(hwsrc=myhwaddress,hwdst=ETHER_BROADCAST,pdst=str(ipdst),psrc=myipaddress)
                arp_reply_packet=srp(arp_request_packet,iface=interface,timeout=1,verbose=False)
                if arp_reply_packet and arp_reply_packet[0]:
                    hw_target = arp_reply_packet[0][0][1].hwsrc
                    print_info('%s is up' % ipdst)

        def arp_request_packet(options):
            #pool threads
            num_th = int(options["threads"][0])
            executr = ThreadPoolExecutor(max_workers=num_th)
            arp_reply_packet = None
            interface = options["interface"][0]
            myhwaddress = get_if_hwaddr(options["interface"][0])
            myipaddress = get_if_addr(options["interface"][0])

            for ipdst in IPNetwork(options["cidr"][0]):
                executr.submit(arp_request, ipdst, myipaddress, myhwaddress, interface)
            executr.shutdown(wait=True)
       
        thread1 = threading.Thread(target=arp_request_packet, args=(self.options,))
        thread1.start()
        thread1.join()
        print_ok("ARP Scan finished")
