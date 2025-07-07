"""
@file       cpu.py
@author     Akshay Joshi
"""

from node import Node
from packet import Packet

class CPU(Node):
    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.__processing_latency = 0

    def add_latency(self, processing_latency: int):
        self.__processing_latency = processing_latency

    def get_latency(self):
        return self.__processing_latency

    def process_pkt(self, pkt: 'Packet'):
        pass

    def advance(self, current_cycle: int):
        super().advance(current_cycle)
        if (self.get_node_id() == "A"):
            msg = self.get_node_id() + str(current_cycle)
            pkt = Packet(str(current_cycle), msg)
            status = self.send_pkt(pkt, "AsendsB")
            if status < 0:
                print(f"[#] ERROR: unable to send pkt {pkt.get_pkt_id()}")
            else:
                print(f"[-] Node '{self.get_node_id()}' sent pkt {pkt.get_pkt_id()}")
        
        pkt = self.recv_pkt("BrecvsA")
        if pkt is not None:
            print(f"[+] Node {self.get_node_id()} received pkt {pkt.get_pkt_id()}")
