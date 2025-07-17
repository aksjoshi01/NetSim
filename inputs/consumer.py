"""
@file       consumer.py
@brief      A consumer node that receives packets and prints them.
"""
import logging
logger = logging.getLogger(__name__)

from node import Node
from plotter import Plotter

class Consumer(Node):
    """
    @class      Consumer
    """
    def __init__(self):
        """
        @brief      A constructor for the Consumer class.
        """
        super().__init__()
        self.pkts_recvd = 0
        self.rate = 4

    def advance(self, cycle):
        """
        @brief      Attempt to receive packets from input ports.
        @param      cycle - an integer representing current simulation time.
        """
        
        self.stats.log_node_activity(self.get_node_id(), cycle, False)
        # if cycle % self.rate  != 0:
        #     return

        for port in self.get_input_ports().values():
            pkt = port.recv_pkt(cycle)
            if pkt:
                logger.info(f"{self.get_node_id()} received packet {pkt.get_pkt_id()} on {port.get_port_id()}")
                self.stats.increment_pkt_recvd(self.get_node_id())
                self.pkts_recvd += 1
                self.stats.log_node_activity(self.get_node_id(), cycle, True)