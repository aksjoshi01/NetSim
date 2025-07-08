"""
@file       simulator.py
@brief      Implements the Simulator class that coordinates the cycle-driven execution.
@author     Akshay Joshi
"""         

from typing import Dict

from node import Node
from link import Link
from packet import Packet
from port import OutputPort, InputPort

class Simulator:
    """
    @class      Simulator
    """
    def __init__(self, max_cycles):
        """
        @brief      A constructor for the Simulator class
        @param      max_cycles - number of cycles the simulation needs to run for
        """
        self.__max_cycles = max_cycles
        self.__nodes: Dict[str, Node] = {}
        self.__links: Dict[str, Link] = {}
        self.__output_ports: Dict[str, OutputPort] = {}
        self.__input_ports: Dict[str, InputPort] = {}

    def add_node(self, node: 'Node'):
        """
        @brief      Adds the node object to its dictionary.
        @param      node - the Node object to be added.
        """
        assert node is not None, "Error: Node cannot be None"
        node_id = node.get_node_id()
        assert node_id not in self.__nodes, f"Error: multiple nodes have same ID {node_id}"
        self.__nodes[node_id] = node

    def add_link(self, link: 'Link'):
        """
        @brief      Adds the link object to its dictionary.
        @param      link - the Link object to be added.
        """
        assert link is not None, "Error: Link cannot be None"
        link_id = link.get_link_id()
        assert link_id not in self.__links, f"Error: multiple links have same ID {link_id}"
        self.__links[link_id] = link

    def add_output_port(self, output_port: 'OutputPort'):
        """
        @brief      Adds the output port object to its dictionary.
        @param      output_port - the OutputPort object to be added.
        """
        assert output_port is not None, "Error: OutputPort cannot be None"
        port_id = output_port.get_port_id()
        assert port_id not in self.__output_ports, f"Error: multiple output ports have same ID {port_id}"
        self.__output_ports[port_id] = output_port

    def add_input_port(self, input_port: 'InputPort'):
        """
        @brief      Adds the input port object to its dictionary.
        @param      input_port - the InputPort object to be added.
        """
        assert input_port is not None, "Error: InputPort cannot be None"
        port_id = input_port.get_port_id()
        assert port_id not in self.__input_ports, "Error: multiple input ports have same ID {port_id}"
        self.__input_ports[input_port.get_port_id()] = input_port

    def run(self):
        """
        @brief      Runs the simulation for `max_cycles`. In each cycle, it calls 
                    the `advance()` method on all registered links and nodes.
        """
        for cycle in range(self.__max_cycles):
            print(f"\n=== Cycle {cycle} ===")

            for link in self.__links.values():
                link.advance(cycle)

            for node in self.__nodes.values():
                node.advance(cycle)
