"""
@file       cpu.py
@brief
@author     Akshay Joshi
"""


from node import Node
from packet import Packet


class CPU(Node):
    """
    @brief
    """
    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.processing_latency = 0


    def add_latency(self, processing_latency: int):
        self.processing_latency = processing_latency


    def process_pkt(self, pkt: 'Packet'):
        pass


    def advance(self, current_cycle: int):
        """
        @brief      Performs some operations every cycle of the simulation
        """
        super().advance(current_cycle)
        if (self.node_id == "A"):
            pkt = Packet(pkt_id = str(current_cycle), src = "A", dst = "B", size = 8, cycle = current_cycle, is_ack = False)
            self.send_pkt(pkt)

        self.recv_pkt()

        for output_port in self.output_ports.values():
            output_port.send_pkt()