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
        self.__cycle = -1

    def set_node_id(self, node_id: str):
        """
        @brief      Assigns the node_id to the Node object.
        @param      node_id - a string representing the ID of the node.
        """
        assert node_id is not None, "Error: node_id cannot be None"
        self.__node_id = node_id

    def get_node_id(self):
        """
        @brief      Returns the node_id of the Node object.
        @return     node_id - a string representing the ID of the node.
        """
        return self.__node_id

    def get_cycle(self):
        """
        @brief      Returns the cycle value.
        @return     cycle - represents the most recent time a pkt was sent.
        """
        return self.__cycle

    def set_cycle(self, cycle):
        """
        @brief      Sets the cycle to the current simulation time.
        @param      cycle - represents the most recent time a pkt was sent.
        """
        self.__cycle = cycle

    def add_input_port(self, input_port):
        """
        @brief      Adds an input port to the node.
        @param      input_port - The input port object to be added.
        @return     0 if operation is successful, -1 otherwise.
        """
        assert input_port.get_port_id() not in self.__input_ports, "Error: cannot add input port with duplicate ID"
        self.__input_ports[input_port.get_port_id()] = input_port

    def add_output_port(self, output_port):
        """
        @brief      Adds an output port to the node.
        @param      output_port - The output port object to be added.
        @return     0 if operation is successful, -1 otherwise.
        """
        assert output_port.get_port_id() not in self.__output_ports, "Error: cannot add output port with duplicate ID"
        self.__output_ports[output_port.get_port_id()] = output_port

    def get_input_ports(self):
        return self.__input_ports

    def get_output_ports(self):
        return self.__output_ports

    def send_pkt(self, pkt: 'Packet', port_id: str, current_cycle: int):
        """
        @brief      Sends a packet to the output port of the node.
        @param      pkt - Packet to be sent.
        @param      port_id - ID of the output port to send the pkt to.
        @param      current_cycle - represents the current simulation time.
        @return     0 on success, -1 otherwise.
        """
        assert pkt is not None, "Error: packet cannot be None"
        assert isinstance(pkt, Packet), "Error; pkt should be of class type Packet"
        assert self.get_cycle() < current_cycle, "Error: cannot send more than 1 pkt in a cycle"

        output_port = self.__output_ports.get(port_id)
        assert output_port is not None, "Error: found None output port"

        status = output_port.send_pkt(pkt, current_cycle)
        if status == 0:
            self.set_cycle(current_cycle)
        return status

    def recv_pkt(self, port_id: str, current_cycle: int):
        """
        @brief      Receives a packet to the input port of the node.
        @param      port_id - ID of the input port to receive the packet from.
        @param      current_cycle - represents the simulation time.
        @return     pkt on success, None otherwise.
        """
        input_port = self.__input_ports.get(port_id)
        if input_port is None:
            return None
        
        pkt = input_port.recv_pkt(current_cycle)
        if pkt is not None:
            return pkt
        
        return None
        
    @abstractmethod
    def advance(self, current_cycle: int):
        pass

    @abstractmethod
    def get_stats(self):
        pass     
