"""
@file       cpu.py
@brief
@author     Akshay Joshi
"""


from NetworkElements.node import Node
from NetworkElements.packet import Packet


class CPU(Node):
    """
    @brief
    """
    def __init__(self, node_id: str, processing_latency: int):
        super().__init__(node_id)
        self.processing_latency = processing_latency


    def process_pkt(self, pkt: 'Packet'):
        pass


    def advance(self, current_cycle: int):
        """
        @brief      Performs some operations every cycle of the simulation
        """