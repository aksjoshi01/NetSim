"""
@file       port.py
@brief      Defines InputPort and OutputPort classes for an input-buffered communication.
@author     Akshay Joshi
"""

from collections import deque

from link import Link
from packet import Packet, CreditPacket

import logging
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

class InputPort(Port):
    """
    @class      InputPort
    """
    def __init__(self, port_id, max_size, link, vc_ids):
        """
        @brief      A constructor for the InputPort class.
        """
        assert isinstance(max_size, int), "Error: max_size should be an integer"
        assert max_size > 0, "Error: max_size should be greater than zero"
        super().__init__(port_id, link)
        self.__max_size = max_size
        self.__fifo = {vc_id: deque() for vc_id in vc_ids}

    def pop_pkt(self, vc_id, current_cycle):
        """
        @brief      Receive the packet from its fifo, if present.
        @param      current_cycle - the current simulation time.
        @return     the received pkt on success, None otherwise.
        """
        fifo = self.__fifo.get(vc_id)
        if len(fifo) > 0:
            connected_link = self.get_connected_link()
            credit_pkt = CreditPacket(vc_id)
            status = connected_link.push_pkt(credit_pkt, current_cycle)
            if status < 0:
                return None
            return fifo.popleft()
        
        return None

    def push_pkt(self, pkt):
        """
        @brief      Pushes the packet to its fifo.
        @param      pkt - the packet to be pushed.
        """
        if len(self.__fifo[pkt.get_vc_id()]) < self.__max_size:
            self.__fifo[pkt.get_vc_id()].append(pkt)


class OutputPort(Port):
    """
    @class      OutputPort
    """
    def __init__(self, port_id, credit, link, vc_ids):
        """
        @brief      A constructor for the OutputPort class.
        """
        assert isinstance(credit, int), "Error: credit should be an integer"
        assert credit > 0, "Error: initial credit should be greater than zero"
        super().__init__(port_id, link)
        self.__recent_sent_cycle = -1
        self.__credit = {vc_id: credit for vc_id in vc_ids}

    def get_credit(self, vc_id):
        assert vc_id in self.__credit, "Error: vc_id not found in credit"
        return self.__credit.get(vc_id)

    def __increment_credit(self, vc_id):
        """
        @brief      Increments the credit by one.
        """
        credit = self.get_credit(vc_id)
        credit += 1
        self.__credit[vc_id] = credit

    def __decrement_credit(self, vc_id):
        """
        @brief      Decrements the credit by one.
        """
        credit = self.get_credit(vc_id)
        credit -= 1
        logger.debug(f"Port '{self.get_port_id()}' sent packet, remaining credit: {credit}")
        self.__credit[vc_id] = credit
        
    def push_pkt(self, pkt, current_cycle):
        """
        @brief      Forwards the pkt to the connected link.
        @param      pkt - packet to be forwarded.
        @param      current_cycle - current simulation time.
        @return     0 on success, -1 otherwise.
        """
        assert pkt is not None, "Error: packet cannot be None"
        assert self.__recent_sent_cycle < current_cycle, "Error: cannot send more than 1 pkt in a cycle"

        # Link calls this method to push credit packet
        if isinstance(pkt, CreditPacket):
            logger.debug(f"Port '{self.get_port_id()}' received credit for vc_id {pkt.get_vc_id()}")
            self.__increment_credit(pkt.get_vc_id())
            return 0
        
        # Node calls this method to push data packet
        available_credits = self.get_credit(pkt.get_vc_id())
        if available_credits > 0:
            connected_link = self.get_connected_link()
            status = connected_link.push_pkt(pkt, current_cycle)
            if status == 0:
                self.__decrement_credit(pkt.get_vc_id())
                self.__recent_sent_cycle = current_cycle
            return status

        return -1