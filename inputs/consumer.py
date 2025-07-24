"""
@file       consumer.py
@brief      A consumer node that receives packets and prints them.
"""
import logging
logger = logging.getLogger(__name__)

from node import Node

class Consumer(Node):
    """
    @class      Consumer
    """
    def __init__(self):
        """
        @brief      A constructor for the Consumer class.
        """
        super().__init__()
        self.rate = 4

    def setup(self):
        self.register_counter_stats(f"pkts_recvd")
        self.register_cycle_stats(f"{self.get_node_id()}")

    def advance(self, cycle):
        """
        @brief      Attempt to receive packets from input ports.
        @param      cycle - an integer representing current simulation time.
        """
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)
        input_port = 'B_in'

        # if cycle % self.rate  != 0:
        #     return

        pkt = self.recv_pkt(input_port, cycle)
        if pkt:
            logger.debug(f"{self.get_node_id()} received packet {pkt.get_pkt_id()} on {input_port}")
            self.incr_counter_stats(f"pkts_recvd", 1)
            self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)