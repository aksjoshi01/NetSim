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
    def __init__(self):
        """
        @brief      A constructor for the Port class.
        """
        self.__port_id = None
        self.__connected_link = None
        self.__cycle = -1

    def set_port_id(self, port_id):
        """
        @brief      Assigns ID to the Port object.
        @param      port_id - string representing ID of the port.
        """
        assert port_id is not None, "Error: port_id cannot be None"
        assert isinstance(port_id, str), "Error: port_id must be a string"
        self.__port_id = port_id

    def get_port_id(self):
        """
        @brief      Returns the port_id of the Port object.
        @return     port_id - a string representing ID of the port.
        """
        return self.__port_id

    def set_connected_link(self, connected_link):
        """
        @brief      Sets the link that connects to the port.
        @param      connected_link - the Link object the connects to the port.
        """
        assert connected_link is not None, "Error: link cannot be None to connect to port"
        self.__connected_link = connected_link

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
    def __init__(self):
        """
        @brief      A constructor for the InputPort class.
        """
        super().__init__()
        self.__fifo_size = None
        self.__fifo: deque[Packet] = deque()

    def set_fifo_size(self, fifo_size):
        """
        @brief      Assigns the max size of the fifo.
        @param      fifo_size - integer value greater than zero.
        """
        assert isinstance(fifo_size, int), "Error: fifo_size should be an integer"
        assert fifo_size > 0, "Error: fifo_size should be greater than zero"
        self.__fifo_size = fifo_size

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
            status = connected_link.send_credit(credit_pkt, current_cycle)
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
    def __init__(self):
        """
        @brief      A constructor for the OutputPort class.
        """
        super().__init__()
        self.__credit = None

    def set_credit(self, credit):
        """
        @brief      Sets the initial credits value.
        @param      credit - an integer value greater than zero.
        """
        assert isinstance(credit, int), "Error: credit should be an integer"
        assert credit > 0, "Error: initial credit should be greater than zero"
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
            status = connected_link.send_pkt(pkt, current_cycle)
            if status == 0:
                self.decrement_credit()
                self.set_cycle(current_cycle)

            return status

        return -1