"""
@file       simulator.py
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


    def add_node(self, node: 'Node'):
        self.nodes[node.get_node_id()] = node

    def add_link(self, link: 'Link'):
        self.links[link.get_link_id()] = link

    def run(self):
        for cycle in range(self.max_cycles):
            print(f"\n=== Cycle {cycle} ===")

            for link in self.links.values():
                link.advance(cycle)

            for node in self.nodes.values():
                node.advance(cycle)


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

    # Create the link
    link_AtoB = Link(link_id = "AtoB", latency = 3)

    # Create ports that serve as endpoints for the link
    nodeA.add_output_port("AsendsB", link_AtoB, link_AtoB.get_latency())
    nodeB.add_input_port("BrecvsA", link_AtoB, link_AtoB.get_latency())

    # Connect output port of A to input port of B
    link_AtoB.add_output_port(nodeA.get_output_port("AsendsB"))
    link_AtoB.add_input_port(nodeB.get_input_port("BrecvsA"))

    # Add the link
    sim.add_link(link_AtoB)

    sim.run()
