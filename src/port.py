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
        self.__port_id = port_id
        self.__connected_link = connected_link

    def get_port_id(self):
        return self.__port_id

    def get_connected_link(self):
        return self.__connected_link


class InputPort(Port):
    def __init__(self, port_id: str, connected_link: 'Link', fifo_size: int):
        super().__init__(port_id, connected_link)
        self.__fifo_size = fifo_size
        self.__fifo: deque[Packet] = deque()

    def recv_pkt(self):
        if len(self.__fifo) > 0:
            connected_link = self.get_connected_link()
            status = connected_link.send_credit()
            if status < 0:
                return None
            return self.__fifo.popleft()
        
        return None

    def recv_from_link(self, pkt: 'Packet'):
        if len(self.__fifo) < self.__fifo_size:
            self.__fifo.append(pkt)


class OutputPort(Port):
    def __init__(self, port_id: str, connected_link: 'Link', credit: int):
        super().__init__(port_id, connected_link)
        self.__credit = credit

    def increment_credit(self):
        self.__credit += 1
        print(f"[^] Port '{self.get_port_id()}' received credit")

    def decrement_credit(self):
        self.__credit -= 1

    def send_pkt(self, pkt: 'Packet'):
        if pkt is None or not isinstance(pkt, Packet):
            return -1

        if self.__credit > 0:
            connected_link = self.get_connected_link()
            status = connected_link.send_pkt(pkt)
            if status == 0:
                self.decrement_credit()

            return status

        return -3