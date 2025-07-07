"""
@file       simulator.py
@author     Akshay Joshi
"""         

from typing import Dict

from node import Node
from link import Link
from packet import Packet

class Simulator:
    def __init__(self, max_cycles):
        self.__max_cycles = max_cycles
        self.__nodes: Dict[str, Node] = {}
        self.__links: Dict[str, Link] = {}

    def add_node(self, node: 'Node'):
        self.__nodes[node.get_node_id()] = node

    def add_link(self, link: 'Link'):
        self.__links[link.get_link_id()] = link

    def run(self):
        for cycle in range(self.__max_cycles):
            print(f"\n=== Cycle {cycle} ===")

            for link in self.__links.values():
                link.advance(cycle)

            for node in self.__nodes.values():
                node.advance(cycle)

