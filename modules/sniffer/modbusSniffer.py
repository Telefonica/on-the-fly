from termcolor import colored, cprint
from module import Module
from otflib.modbusTCPFrame import *
from scapy.all import *
import threading
import time
from printib import * 
from datetime import datetime
import os


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "Modbus Packet Sniffer",
                       "Description": "Modbus Packet Sniffer",
                       "Author": "Luis Eduardo Álvarez @luisedev, @pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = { "rport":        ["502", "Target Port", True],
                    "interface":    ["eth0", "Interface for sniffing", True],
                    "output":       ["decimal", "Output info. type: Could be decimal, hex, bytes, all", True],
                    "verbose":       ["True", "Display info or not (verbose mode) [True | False]", True],
                    "savePcap":     ["False", "Saves a .pcap file with the current sniff [True | False]", False]}

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

        def go(options):
            verbose = options["verbose"][0] == "True"
            savePcap = options["savePcap"][0] == "True"
            if savePcap:
                print_info("Saving PCAP File at: "+ str(os.getcwd()))
                name = "mySniffedPackets"
                time = str(datetime.now())
                ext = ".pcap"
                filename = name+time+ext
                myPcap = PcapWriter(filename, append=True,sync=True)

            def print_packet(packet):
                print_info("Origin IP Address: %s" % packet[IP].src)
                print_info("Origin Port: %s" % packet[TCP].sport)
                print_info("Destination IP Address: %s" % packet[IP].dst)
                print_info("Destination Port: %s" % packet[TCP].dport)

            def packet_callback(packet):            
                if packet.haslayer(TCP):
                    if len(packet[TCP].payload) > 0:
                        if savePcap:
                            myPcap.write(packet)
                        #Check packet type: Request or Response
                        if str(packet.sport) == options["rport"][0]:
                            if verbose:
                                print_info("\nNEW RESPONSE PACKET:")
                            modbus_packet = modbusTCPFrame(packet = packet, type = "Response")
                        if str(packet.dport) == options["rport"][0]:
                            if verbose:
                                print_info("\nNEW REQUEST PACKET:")
                            modbus_packet = modbusTCPFrame(packet = packet,type = "Request")
                        if verbose:
                            print_packet(packet)
                        modbus_packet.processData()
                        #Check output type to print: hex, decimal, bytes or verbose
                        if options["output"][0]=="hex" and verbose:
                            modbus_packet.showDataHEX()
                        elif options["output"][0]=="decimal" and verbose:
                            modbus_packet.showDataDecimal()
                        elif options["output"][0]=="bytes" and verbose:
                            modbus_packet.showDataBytes()
                        elif options["output"][0]=="all" and verbose:
                            modbus_packet.showDataHEX()
                            modbus_packet.showDataDecimal()
                            modbus_packet.showDataBytes()
                        elif verbose:
                            print_error("%s not valid value" % options["output"][0])
                            
                            
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                try:
                    sniff(iface=options["interface"][0],filter="tcp port %s" % options["rport"][0], prn=packet_callback, store=0, stop_filter=lambda p: e.is_set())
                except Exception as exc:
                    print_error(str(exc))
                    return False

        e = threading.Event()
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start()
        thread2 = threading.Thread(target=control, args=(e,thread1,))
        thread2.start()
       
        super(CustomModule, self).run(t=thread2)
