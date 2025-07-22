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

    def initialize(self):
        self.get_stats().register_counter(f"pkts_recvd")
        self.get_stats().register_cycle_map(f"{self.get_node_id()}")

    def advance(self, cycle):
        """
        @brief      Attempt to receive packets from input ports.
        @param      cycle - an integer representing current simulation time.
        """
        self.get_stats().record_cycle(f"{self.get_node_id()}", cycle, False)

        if cycle % self.rate  != 0:
            return

        input_ports = self.get_input_ports()
        input_port = next(iter(input_ports.values()))

        pkt = self.recv_pkt(input_port.get_port_id(), cycle)
        if pkt:
            logger.info(f"{self.get_node_id()} received packet {pkt.get_pkt_id()} on {input_port.get_port_id()}")
            self.incr_counter(f"pkts_recvd", 1)
            self.record_cycle(f"{self.get_node_id()}", cycle, True)

    def finalize(self):
        logger.info(f"Node {self.get_node_id()} stats:")
        self.get_stats().dump_summary()
        logger.info(f"\n")