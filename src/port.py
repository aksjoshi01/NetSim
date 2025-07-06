"""
@file       port.py
@author     Akshay Joshi
"""

from collections import deque
from typing import List

from link import Link
from packet import Packet

class Port:
    def __init__(self, port_id: str, connected_link: 'Link'):
        self.port_id = port_id
        self.connected_link = connected_link


class InputPort(Port):
    def __init__(self, port_id: str, connected_link: 'Link', fifo_size: int):
        super().__init__(port_id, connected_link)
        self.fifo_size = fifo_size
        self.fifo: deque[Packet] = deque()


    def recv_pkt(self):
        if len(self.fifo) > 0:
            status = self.connected_link.send_credit()
            if status < 0:
                return None
            return self.fifo.popleft()
        
        return None


    def recv_from_link(self, pkt: 'Packet'):
        if len(self.fifo) < self.fifo_size:
            self.fifo.append(pkt)


class OutputPort(Port):
    def __init__(self, port_id: str, connected_link: 'Link', credit: int):
        super().__init__(port_id, connected_link)
        self.credit = credit


    def increment_credit(self):
        self.credit += 1
        print(f"[^] Port '{self.port_id}' received credit")


    def decrement_credit(self):
        self.credit -= 1


    def send_pkt(self, pkt: 'Packet'):
        if pkt is None or not isinstance(pkt, Packet):
            return -1

        if self.credit > 0:
            status = self.connected_link.send_pkt(pkt)
            if status == 0:
                self.decrement_credit()

            return status

        return -3