"""
@file       cpu.py
@brief      Defines the CPU class that represents a processing node in the network.
@author     Akshay Joshi
"""
import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet

class CPU(Node):
    """
    @class      CPU
    """
    def __init__(self):
        """
        @brief      A constructor for the CPU class.
        """
        super().__init__()

    def advance(self, current_cycle: int):
        """
        @brief      Attempts to send a packet every clock, as well as receive incoming packets.
        @param      current_cycle - current simulation time.
        """
        super().advance(current_cycle)
        if self.get_node_id() == "A":
            msg = self.get_node_id() + str(current_cycle)
            pkt = Packet(str(current_cycle), msg)
            status = self.send_pkt(pkt, "AsendsB", current_cycle)
            if status < 0:
                logger.warning(f"Node {self.get_node_id()} unable to send pkt {pkt.get_pkt_id()}")
            else:
                logger.info(f"Node '{self.get_node_id()}' sent pkt {pkt.get_pkt_id()}")
        
        pkt = self.recv_pkt("BrecvsA", current_cycle)
        if pkt is not None:
            logger.info(f"Node {self.get_node_id()} received pkt {pkt.get_pkt_id()}")
