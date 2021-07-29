from termcolor import colored, cprint
from module import Module
from concurrent.futures import ThreadPoolExecutor
from scapy.all import *
from printib import *
import time

class CustomModule(Module):
    def __init__(self):
        information = { "Name"       : "SYN_scan",
                        "Description": "A simple and faster SYN scanner",
                        "Author"     : "roberaranda"}

        # -----------name-----default_value--description--required?
        options = { "target"    : ["127.0.0.1", "Target IP", True],
                    "ports"     : ["80,443", "Ports to be scanned", True],
                    "threads"   : ["1", "Number of threads used in the scan", True],
                    "sport"     : [None, "Source port. A random port is selected by default", False]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def scan(target, sport, port):
            packet = sr1(IP(dst=target)/TCP(sport=sport, dport=port, flags="S"), timeout=1, verbose=0)
            if packet == None:
                print_info(f"No response when scanning port {port}. Host seems down.")
                return
            if packet.haslayer(TCP):
                if packet[TCP].flags == "SA":
                    print_info(f"Port {port} is open")
                    return
                # If response is "RA" the port is closed
                elif packet[TCP].flags != "RA":
                    print_info(f"Port {port} seems filtered. Response flag: {packet[TCP].flags}")
                    return
            else:
                print_info(f"Unknown response scanning port {port}. Here is the summary:\n{packet.summary()}")

        def threadspool(target, ports, sport, threads):
            # Creating the pool of threads
            executor = ThreadPoolExecutor(max_workers=threads)
            # Submiting a task for each port to the threads pool
            # When a thread is finished it will take another task with a new port
            t = threading.currentThread()
            for port in ports:
                f = executor.submit(scan, target, sport, port)
            executor.shutdown(wait=True)

        # setting parameters from user's inputs
        target  = self.options["target"][0]
        threads = int(self.options["threads"][0])
        sport   = RandShort() if (self.options["sport"][0] == None) else self.options["sport"][0]
        ports   = self.options["ports"][0]
        if "," in ports:
            ports = [int(port) for port in ports.split(",")]
        elif "-" in ports:
            pbegin, pend = ports.split("-")
            ports = list(range(int(pbegin), int(pend)))
        else:
            ports = list(ports)
        thread1 = threading.Thread(target=threadspool, args=(target, ports, sport, threads,))
        thread1.start()
        thread1.join()
        print_ok("SYN Scan finished")
