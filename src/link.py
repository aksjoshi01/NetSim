"""
@file       link.py
@author     Akshay Joshi
"""

from collections import deque
from typing import Optional

from packet import Packet

class Link:
    def __init__(self, link_id: str, latency: int):
        self.__link_id = link_id
        self.__output_port = None
        self.__input_port = None
        self.__latency = latency
        self.__pipeline: deque[Optional[Packet]] = deque([None] * latency)
        self.__credit_pipeline: deque[bool] = deque([False] * latency)

    def add_output_port(self, output_port: 'OutputPort'):
        self.__output_port = output_port

    def add_input_port(self, input_port: 'InputPort'):
        self.__input_port = input_port

    def get_link_id(self):
        return self.__link_id

    def get_latency(self):
        return self.__latency

    def send_pkt(self, pkt: 'Packet'):
        if pkt is None or not isinstance(pkt, Packet):
            return -1
        
        if self.__pipeline[-1] is None:
            self.__pipeline[-1] = pkt
            return 0

        return -2

    def send_credit(self):
        if self.__credit_pipeline[-1] is False:
            self.__credit_pipeline[-1] = True
            return 0

        return -2

    def advance(self, current_cycle: int):
        # Advance the packets
        pkt = self.__pipeline.popleft()
        if pkt is not None:
            self.__input_port.recv_from_link(pkt)
        self.__pipeline.append(None)

        # Advance the credits
        if self.__credit_pipeline.popleft():
            self.__output_port.increment_credit()
        self.__credit_pipeline.append(False)