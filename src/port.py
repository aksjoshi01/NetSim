"""
@file       port.py
@brief      Defines InputPort and OutputPort classes for an input-buffered communication.
@author     Akshay Joshi
"""

import logging
from collections import deque

from link import Link
from packet import Packet, CreditPacket

logger = logging.getLogger(__name__)

class Port:
    """
    @class      Port
    """
    def __init__(self, port_id, link):
        """
        @brief      A constructor for the Port class.
        """
        assert port_id is not None, "Error: port_id cannot be None"
        assert isinstance(port_id, str), "Error: port_id must be a string"
        assert link is not None, "Error: link cannot be None to connect to port"
        assert isinstance(link, Link), "Error: link should be of type class Link"

        self.__port_id = port_id
        self.__connected_link = link
        self.__cycle = -1

    def get_port_id(self):
        """
        @brief      Returns the port_id of the Port object.
        @return     port_id - a string representing ID of the port.
        """
        return self.__port_id

    def get_connected_link(self):
        """
        @brief      Returns the Link object the connects the port.
        @return     connected_link - the Link object.
        """
        return self.__connected_link

    def set_cycle(self, cycle):
        """
        @brief      Assigns cycle to the most recent time a pkt was sent.
        @param      cycle - an integer representing most recent time a pkt was sent.
        """
        self.__cycle = cycle

    def get_cycle(self):
        """
        @brief      Returns the most recent cycle a pkt was sent.
        @return     cycle - an integer representing most recent time a pkt was sent.
        """
        return self.__cycle


class InputPort(Port):
    """
    @class      InputPort
    """
    def __init__(self, port_id, fifo_size, link):
        """
        @brief      A constructor for the InputPort class.
        """
        assert isinstance(fifo_size, int), "Error: fifo_size should be an integer"
        assert fifo_size > 0, "Error: fifo_size should be greater than zero"
        super().__init__(port_id, link)
        self.__fifo_size = fifo_size
        self.__fifo: deque[Packet] = deque()

    def get_fifo_size(self):
        return self.__fifo_size

    def get_fifo(self):
        return self.__fifo

    def recv_pkt(self, current_cycle: int):
        """
        @brief      Receive the packet from its fifo, if present.
        @param      current_cycle - the current simulation time.
        @return     the received pkt on success, None otherwise.
        """
        fifo = self.get_fifo()
        
        if len(fifo) > 0:
            connected_link = self.get_connected_link()
            credit_pkt = CreditPacket()
            status = connected_link.push_pkt(credit_pkt, current_cycle, "credit")
            if status < 0:
                return None
            return fifo.popleft()
        
        return None

    def recv_from_link(self, pkt: 'Packet'):
        """
        @brief      Pushes the packet to its fifo.
        @param      pkt - the packet to be pushed.
        """
        fifo = self.get_fifo()

        if len(fifo) < self.get_fifo_size():
            fifo.append(pkt)


class OutputPort(Port):
    """
    @class      OutputPort
    """
    def __init__(self, port_id, credit, link):
        """
        @brief      A constructor for the OutputPort class.
        """
        assert isinstance(credit, int), "Error: credit should be an integer"
        assert credit > 0, "Error: initial credit should be greater than zero"
        super().__init__(port_id, link)
        self.__credit = credit

    def get_credit(self):
        return self.__credit

    def increment_credit(self):
        """
        @brief      Increments the credit by one.
        """
        self.__credit += 1
        logger.debug(f"Port '{self.get_port_id()}' received credit")

    def decrement_credit(self):
        """
        @brief      Decrements the credit by one.
        """
        self.__credit -= 1

    def send_pkt(self, pkt: 'Packet', current_cycle: int):
        """
        @brief      Forwards the pkt to the connected link.
        @param      pkt - packet to be forwarded.
        @param      current_cycle - current simulation time.
        @return     0 on success, -1 otherwise.
        """
        assert pkt is not None, "Error: packet cannot be None"
        assert isinstance(pkt, Packet), "Error: pkt should be of class type Packet"
        assert self.get_cycle() < current_cycle, "Error: cannot send more than 1 pkt in a cycle"

        if self.get_credit() > 0:
            connected_link = self.get_connected_link()
            status = connected_link.push_pkt(pkt, current_cycle, "data")
            if status == 0:
                self.decrement_credit()
                self.set_cycle(current_cycle)

            return status

        return -10