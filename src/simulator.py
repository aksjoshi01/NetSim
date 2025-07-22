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
        logger.info("===== Simulation =====")
        for node in self.__nodes.values():
            node.setup()

    def run(self):
        """
        @brief      Runs the simulation for `max_cycles`. In each cycle, it calls 
                    the `advance()` method on all registered links and nodes.
        """
        self.setup()

        for cycle in range(self.__max_cycles):
            logger.info(f"=== Cycle {cycle} ===")

            for link in self.__links.values():
                link.advance(cycle)

            for node in self.__nodes.values():
                node.advance(cycle)
            logger.info(f"\n")

        print(f"Simulation completed. \nLog files, statistics and plots can be found in ../outputs/ directory")
        self.teardown()

    def teardown(self):
        logger.info(f"===== Statistics =====")
        for node in self.__nodes.values():
            node.teardown()

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
        
        for row in parser.get_node_specs():
            module_name = row["module"]
            class_name = row["class"]
            node_id = row["node_id"]

            user_module = importlib.import_module(module_name)
            NodeClass = getattr(user_module, class_name)
            
            node = NodeClass()
            node.set_node_id(node_id)
            self.add_node(node)

    def build_connections(self, parser):
        """
        @brief      Instantiates the output ports, input ports and links and connects them.
        @param      parser - parsed data that contains the topology of the network.
        """
        for row in parser.get_connection_specs():
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
            
            src_node = self.get_node(src_node_id)
            dst_node = self.get_node(dst_node_id)

            link_id = f"link_{src_node_id}_{output_port_id}_to_{dst_node_id}_{input_port_id}"
            link = Link(link_id, latency)

            output_port = OutputPort(output_port_id, credit, link)
            input_port = InputPort(input_port_id, fifo_size, link)

            link.set_output_port(output_port)
            link.set_input_port(input_port)

            src_node.add_output_port(output_port)
            dst_node.add_input_port(input_port)

            self.add_link(link)
