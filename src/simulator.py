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
    def __init__(self, max_cycles, parser):
        """
        @brief      A constructor for the Simulator class
        @param      max_cycles - number of cycles the simulation needs to run for
        """
        self.__max_cycles = max_cycles
        self.__parser = parser
        self.__nodes: Dict[str, Node] = {}
        self.__links: Dict[str, Link] = {}

    def add_node(self, node: 'Node'):
        """
        @brief      Adds the node object to its dictionary.
        @param      node - the Node object to be added.
        """
        assert node is not None, "Error: Node cannot be None"
        node_id = node.get_node_id()
        assert node_id not in self.__nodes, f"Error: multiple nodes have same ID {node_id}"
        self.__nodes[node_id] = node

    def get_node(self, node_id):
        return self.__nodes[node_id]

    def add_link(self, link: 'Link'):
        """
        @brief      Adds the link object to its dictionary.
        @param      link - the Link object to be added.
        """
        assert link is not None, "Error: Link cannot be None"
        link_id = link.get_link_id()
        assert link_id not in self.__links, f"Error: multiple links have same ID {link_id}"
        self.__links[link_id] = link


    def setup(self):
        self.__parser.parse()
        self.build_nodes()
        self.build_connections()

        logger.debug("===== Simulation =====")
        for node in self.__nodes.values():
            node.setup()

    def run(self):
        """
        @brief      Runs the simulation for `max_cycles`. In each cycle, it calls 
                    the `advance()` method on all registered links and nodes.
        """
        for cycle in range(self.__max_cycles):
            logger.debug(f"=== Cycle {cycle} ===")

            for link in self.__links.values():
                link.advance(cycle)

            for node in self.__nodes.values():
                node.advance(cycle)
            logger.debug(f"\n")

        print(f"Simulation completed. \nLog files, statistics and plots can be found in ../outputs/ directory")

    def teardown(self):
        logger.info(f"===== Statistics =====")
        for node in self.__nodes.values():
            node.teardown()

    def build_nodes(self):
        """
        @brief      Instantiates the nodes based on the information from the parsed data.
        @param      parser - parsed data that contains information about the nodes.
        @param      user_nodes_dir  - path to the directory that contains user nodes that is 
                    used to tell the system to include the specified directory when looking 
                    for modules.
        """
        for node_setup in self.__parser.nodes:
            user_module = importlib.import_module(node_setup.get_module_name())
            NodeClass = getattr(user_module, node_setup.get_class_name())
            
            node = NodeClass()
            node.set_node_id(node_setup.get_node_id())
            self.add_node(node)


    def build_connections(self):
        """
        @brief      Instantiates the output ports, input ports and links and connects them.
        @param      parser - parsed data that contains the topology of the network.
        """
        for data in self.__parser.connections:
            src_node = self.get_node(data.get_src_node())
            dst_node = self.get_node(data.get_dst_node())

            link = Link(data.get_link_id(), data.get_latency(), data.get_vc_ids())

            output_port = OutputPort(data.get_op_id(), data.get_credit(), link, data.get_vc_ids())
            input_port = InputPort(data.get_ip_id(), data.get_fifo_size(), link, data.get_vc_ids())

            link.set_output_port(output_port)
            link.set_input_port(input_port)

            src_node.add_output_port(output_port)
            dst_node.add_input_port(input_port)

            self.add_link(link)