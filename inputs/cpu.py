"""
@file       cpu.py
@author     Akshay Joshi
"""

from node import Node
from packet import Packet

class CPU(Node):
    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.processing_latency = 0

    def add_latency(self, processing_latency: int):
        self.processing_latency = processing_latency

    def process_pkt(self, pkt: 'Packet'):
        pass

    def advance(self, current_cycle: int):
        super().advance(current_cycle)
        if (self.node_id == "A"):
            msg = self.node_id + str(current_cycle)
            pkt = Packet(pkt_id = str(current_cycle), message = msg)
            status = self.send_pkt(pkt, "AsendsB")
            if status < 0:
                print(f"[#] ERROR: unable to send pkt {pkt.pkt_id}")
            else:
                print(f"[-] Node '{self.node_id}' sent pkt {pkt.pkt_id}")
        
        pkt = self.recv_pkt("BrecvsA")
        if pkt is not None:
            print(f"[+] Node {self.node_id} received pkt {pkt.pkt_id}")
