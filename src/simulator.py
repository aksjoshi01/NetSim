"""
@file       simulator.py
@brief      Implements the Simulator class that coordinates the cycle-driven execution.
@author     Akshay Joshi
"""         

import os
import importlib
import logging
from typing import Dict

from node import Node
from link import Link
from packet import Packet
from port import OutputPort, InputPort
from parser import Parser
from stats import Stats

logger = logging.getLogger(__name__)

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
        self.stats = Stats()

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

    def initialize(self):
        for node in self.__nodes.values():
            node.initialize()

    def run(self):
        """
        @brief      Runs the simulation for `max_cycles`. In each cycle, it calls 
                    the `advance()` method on all registered links and nodes.
        """
        for cycle in range(self.__max_cycles):
            logger.info(f"=== Cycle {cycle} ===")

            for link in self.__links.values():
                link.advance(cycle)

            for node in self.__nodes.values():
                node.advance(cycle)
            logger.info(f"\n")

        self.stats.dump_summary()
        print(f"Simulation completed. \nLog files, statistics and plots can be found in ../outputs/ directory")

    def build_nodes(self, parser, user_nodes_dir):
        """
        @brief      Instantiates the nodes based on the information from the parsed data.
        @param      parser - parsed data that contains information about the nodes.
        @param      user_nodes_dir  - path to the directory that contains user nodes that is 
                    used to tell the system to include the specified directory when looking 
                    for modules.
        """
        if user_nodes_dir not in os.sys.path:
            os.sys.path.append(user_nodes_dir)
        
        for row in parser.node_specs:
            module_name = row["module"]
            class_name = row["class"]
            node_id = row["node_id"]

            user_module = importlib.import_module(module_name)
            NodeClass = getattr(user_module, class_name)
            
            node = NodeClass()
            node.set_node_id(node_id)
            node.set_stats(self.stats)
            self.add_node(node)

    def build_connections(self, parser):
        """
        @brief      Instantiates the output ports, input ports and links and connects them.
        @param      parser - parsed data that contains the topology of the network.
        """
        for row in parser.connection_specs:
            src_node_id = row["src_node"]
            dst_node_id = row["dst_node"]
            output_port_id = row["src_port"]
            input_port_id = row["dst_port"]
            
            try:
                credit = int(row["credit"])
                fifo_size = int(row["fifo_size"])
                latency = int(row["latency"])
            except ValueError:
                raise ValueError(f"Invalid integer")
            
            src_node = self.__nodes[src_node_id]
            dst_node = self.__nodes[dst_node_id]

            link = Link()
            link_id = f"link_{src_node_id}_{output_port_id}_to_{dst_node_id}_{input_port_id}"
            link.set_link_id(link_id)
            link.set_latency(latency)
            link.init_fifos()

            output_port = OutputPort()
            output_port.set_port_id(output_port_id)
            output_port.set_credit(credit)
            output_port.set_connected_link(link)

            input_port = InputPort()
            input_port.set_port_id(input_port_id)
            input_port.set_fifo_size(fifo_size)
            input_port.set_connected_link(link)

            link.set_output_port(output_port)
            link.set_input_port(input_port)

            src_node.add_output_port(output_port)
            dst_node.add_input_port(input_port)

            self.add_output_port(output_port)
            self.add_input_port(input_port)
            self.add_link(link)
