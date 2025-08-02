"""
@file       node.py
@brief      Defines the Node class, which models processing elements in the network.
@author     Akshay Joshi
"""

from typing import Dict
from collections import deque
from abc import abstractmethod

from port import OutputPort, InputPort
from packet import Packet
from stats import Stats

import logging
logger = logging.getLogger(__name__)

class Node:
    """
    @class      Node
    """
    def __init__(self):
        """
        @brief      A constructor for the Node class.
        """
        self.__node_id = None
        self.__input_ports: Dict[str, 'InputPort'] = {}
        self.__output_ports: Dict[str, 'OutputPort'] = {}
        self.__last_sent_cycle = -1
        self.__stats = Stats()

    def set_node_id(self, node_id):
        """
        @brief      Assigns the node_id to the Node object.
        @param      node_id - a string representing the ID of the node.
        """
        assert node_id is not None, "Error: node_id cannot be None"
        assert isinstance(node_id, str), "Error: node_id should be a string"
        self.__node_id = node_id

    def get_node_id(self):
        """
        @brief      Returns the node_id of the Node object.
        @return     node_id - a string representing the ID of the node.
        """
        return self.__node_id

    def add_input_port(self, input_port):
        """
        @brief      Adds an input port to the node.
        @param      input_port - The input port object to be added.
        @return     0 if operation is successful, -1 otherwise.
        """
        assert input_port is not None, "Error: input_port cannot be None"
        assert input_port.get_port_id() not in self.__input_ports, "Error: cannot add input port with duplicate ID"
        self.__input_ports[input_port.get_port_id()] = input_port

    def add_output_port(self, output_port):
        """
        @brief      Adds an output port to the node.
        @param      output_port - The output port object to be added.
        @return     0 if operation is successful, -1 otherwise.
        """
        assert output_port is not None, "Error: output_port cannot be None"
        assert output_port.get_port_id() not in self.__output_ports, "Error: cannot add output port with duplicate ID"
        self.__output_ports[output_port.get_port_id()] = output_port

    def get_input_port(self, port_id):
        assert port_id in self.__input_ports, "Error: invalid port_id given"
        return self.__input_ports[port_id]

    def get_output_port(self, port_id):
        assert port_id in self.__output_ports, "Error: invalid port_id given"
        return self.__output_ports[port_id]

    def send_pkt(self, pkt, port_id, current_cycle):
        """
        @brief      Sends a packet to the output port of the node.
        @param      pkt - Packet to be sent.
        @param      port_id - ID of the output port to send the pkt to.
        @param      current_cycle - represents the current simulation time.
        @return     0 on success, -1 otherwise.
        """
        assert pkt is not None, "Error: packet cannot be None"
        assert isinstance(pkt, Packet), "Error; pkt should be of class type Packet"
        assert self.__last_sent_cycle < current_cycle, "Error: cannot send more than 1 pkt in a cycle"

        output_port = self.get_output_port(port_id)
        assert output_port is not None, "Error: found None output port"

        status = output_port.push_pkt(pkt, current_cycle)
        if status == 0:
            self.__last_sent_cycle = current_cycle
        return status

    def recv_pkt(self, port_id, vc_id, current_cycle):
        """
        @brief      Receives a packet to the input port of the node.
        @param      port_id - ID of the input port to receive the packet from.
        @param      current_cycle - represents the simulation time.
        @return     pkt on success, None otherwise.
        """
        input_port = self.get_input_port(port_id)
        if input_port is None:
            return None
        
        pkt = input_port.pop_pkt(vc_id, current_cycle)
        if pkt is not None:
            return pkt
        
        return None

    def get_stats(self):
        return self.__stats

    def register_counter_stats(self, name):
        self.get_stats().register_counter(name)

    def register_cycle_stats(self, name):
        self.get_stats().register_cycle(name)

    def register_interval_counter_stats(self, name, interval):
        self.get_stats().register_interval_counter(name, interval)

    def incr_counter_stats(self, name, amount):
        self.get_stats().incr_counter(name, amount)

    def record_cycle_stats(self, name, cycle, val):
        self.get_stats().record_cycle(name, cycle, val)

    def incr_interval_counter_stats(self, name, cycle, amount):
        self.get_stats().incr_interval_counter(name, cycle, amount)

    def teardown(self):
        logger.info(f"Node {self.get_node_id()} stats:")
        self.get_stats().dump_summary()
        logger.info(f"\n")

    @abstractmethod
    def advance(self, current_cycle: int):
        pass

    @abstractmethod
    def setup(self):
        pass

