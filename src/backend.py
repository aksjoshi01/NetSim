"""
@file       backend.py
@brief      Provides the backend interface for building and executing custom simulations.
@author     Akshay Joshi
"""

import os

from node import Node
from link import Link
from packet import Packet
from port import OutputPort, InputPort
from simulator import Simulator
from parser import Parser

if __name__ == "__main__":
    """
    @brief      The simulation runs for 30 cycles. 2 nodes are instantiated
                dynamically from CPU class and a link is created between them. 
                Node A has 1 output port and Node B has 1 input port. 
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, "..", "config")
    user_nodes_dir = os.path.join(base_dir, "..", "inputs")

    parser = Parser(config_dir)
    parser.parse()

    sim = Simulator(30)
    sim.build_nodes(parser, user_nodes_dir)
    sim.build_connections(parser)
    sim.run()