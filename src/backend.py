"""
@file       backend.py
@author     Akshay Joshi
"""

import importlib
import os
import sys

from node import Node
from link import Link
from packet import Packet
from simulator import Simulator

if __name__ == "__main__":
    sim = Simulator(30)

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
        sys.exit(-1)

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