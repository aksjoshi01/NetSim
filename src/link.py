"""
@file       link.py
@author     Akshay Joshi
"""

from collections import deque
from typing import Optional

from packet import Packet

class Link:
    def __init__(self, link_id: str, latency: int):
        self.link_id = link_id
        self.output_port = None
        self.input_port = None
        self.latency = latency
        self.pipeline: deque[Optional[Packet]] = deque([None] * latency)
        self.credit_pipeline: deque[bool] = deque([False] * latency)

    
    def add_output_port(self, output_port: 'OutputPort'):
        self.output_port = output_port


    def add_input_port(self, input_port: 'InputPort'):
        self.input_port = input_port

    
    def get_link_id(self):
        return self.link_id


    def get_latency(self):
        return self.latency


    def send_pkt(self, pkt: 'Packet'):
        if pkt is None or not isinstance(pkt, Packet):
            return -1
        
        if self.pipeline[-1] is None:
            self.pipeline[-1] = pkt
            return 0

        return -2


    def send_credit(self):
        if self.credit_pipeline[-1] is False:
            self.credit_pipeline[-1] = True
            return 0

        return -2


    def advance(self, current_cycle: int):
        # Advance the packets
        pkt = self.pipeline.popleft()
        if pkt is not None:
            self.input_port.recv_from_link(pkt)
        self.pipeline.append(None)

        # Advance the credits
        if self.credit_pipeline.popleft():
            self.output_port.increment_credit()
        self.credit_pipeline.append(False)