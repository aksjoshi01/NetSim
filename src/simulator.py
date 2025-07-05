"""
@file       simulator.py
@brief      A cycle-accurate network simulator
@author     Akshay Joshi
"""         


from collections import deque
from typing import Dict, List, Optional

from node import Node
from link import Link
from packet import Packet

import importlib
import os
import sys


class Simulator:
    """
    @class      Simulator
    @brief      A simple network simulator that manages nodes and links. The simulator allows adding nodes and links, 
                and simulates the network operation over a specified number of cycles. 
    """

    def __init__(self, max_cycles):
        self.max_cycles = max_cycles
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[str, Link] = {}
        self.current_cycle = 0


    def add_node(self, node: 'Node'):
        """
        @brief      Add a node to the simulator
        @param      node - Node instance to be added
        """
        self.nodes[node.node_id] = node

    def add_link(self, link: 'Link'):
        """
        @brief      Add a link to the simulator
        @param      link - Link instance to be added
        """
        self.links[link.link_id] = link

    def run(self):
        """
        @brief      Run the simulator for a specified number of cycles. 
                    During each cycle, the simulator wakes up each link and node to perform their operations.
        """
        for cycle in range(self.max_cycles):
            print(f"\n=== Cycle {cycle} ===")

            for link in self.links.values():
                link.advance(cycle)

            for node in self.nodes.values():
                node.advance(cycle)

            self.current_cycle += 1    


if __name__ == "__main__":
    sim = Simulator(max_cycles = 30)

    # Hardcode the file path and class name for now
    user_nodes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs")
    sys.path.append(user_nodes_dir)

    # List of user-defined nodes to instantiate
    user_node_configurations = [
        {"module": "cpu", "class": "CPU", "id": "A"},
        {"module": "cpu", "class": "CPU", "id": "B"},
    ]

    instantiated_nodes = {}

    for config in user_node_configurations:
        module_name = config["module"]
        class_name = config["class"]
        node_id = config["id"]

        try:
            user_module = importlib.import_module(module_name)
            UserNodeClass = getattr(user_module, class_name)
            new_node = UserNodeClass(node_id)
            sim.add_node(new_node)
            instantiated_nodes[node_id] = new_node

        except (ImportError, AttributeError) as e:
            print(f"Error loading user-defined node '{node_id}' from module '{module_name}' class '{class_name}': {e}")
            sys.exit(1)

    nodeA = instantiated_nodes.get("A")
    nodeB = instantiated_nodes.get("B")

    if not (nodeA and nodeB):
        print("Error: Could not find node A and/or node B after dynamic loading. Exiting.")
        sys.exit(1)

    # Create the link between the nodes
    link_AtoB = Link("A-to-B", None, None, latency = 3)
    link_BtoA = Link("B-to-A", None, None, latency = 3)

    # Create ports for node A
    nodeA.add_output_port("B", link_AtoB, 2 * link_AtoB.get_latency())
    nodeA.add_input_port("B", link_BtoA, 2 * link_BtoA.get_latency())

    # Create ports for node B
    nodeB.add_output_port("A", link_BtoA, 2 * link_BtoA.get_latency())
    nodeB.add_input_port("A", link_AtoB, 2 * link_AtoB.get_latency())

    # Connect output port of A to input port of B
    link_AtoB.add_src(nodeA.get_output_port("B"))
    link_AtoB.add_dst(nodeB.get_input_port("A"))

    # Connect output port of B to input port of A
    link_BtoA.add_src(nodeB.get_output_port("A"))
    link_BtoA.add_dst(nodeA.get_input_port("B"))

    # Add all the links
    sim.add_link(link_AtoB)
    sim.add_link(link_BtoA)

    sim.run()
