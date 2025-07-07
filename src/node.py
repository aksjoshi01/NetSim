"""
@file       node.py
@author     Akshay Joshi
"""

from collections import deque
from typing import Dict, List, Optional
from abc import abstractmethod

from port import OutputPort, InputPort
from packet import Packet

class Node:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.input_ports: Dict[str, 'InputPort'] = {}
        self.output_ports: Dict[str, 'OutputPort'] = {}

    def get_node_id(self):
        return self.node_id

    def add_input_port(self, port_id: str, link: 'Link', fifo_size: int):
        self.input_ports[port_id] = InputPort(port_id, link, fifo_size)

    def add_output_port(self, port_id: str, link: 'Link', credit: int):
        self.output_ports[port_id] = OutputPort(port_id, link, credit)

    def get_output_port(self, port_id: str):
        return self.output_ports[port_id]

    def get_input_port(self, port_id: str):
        return self.input_ports[port_id]

    def send_pkt(self, pkt: 'Packet', port_id: str):
        if pkt is None or not isinstance(pkt, Packet):
            return -1
       
        output_port = self.output_ports.get(port_id)
        if output_port is None:
            return -3

        return output_port.send_pkt(pkt)

    def recv_pkt(self, port_id: str):
        input_port = self.input_ports.get(port_id)
        if input_port is None:
            return None
        
        pkt = input_port.recv_pkt()
        if pkt is not None:
            return pkt
        
        return None
        
    @abstractmethod
    def process_pkt(self, pkt: 'Packet'):
        pass

    @abstractmethod
    def advance(self, current_cycle: int):
        pass
        
