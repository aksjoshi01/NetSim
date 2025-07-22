"""
@file       producer.py
@brief      A producer node that generates a packet every cycle and sends it to its output port.
"""

import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet

class Producer(Node):
    """
    @class      Producer
    """
    def __init__(self):
        """
        @brief      A constructor for the Producer class
        """
        super().__init__()

    def setup(self):
        self.get_stats().register_counter(f"pkts_sent")
        self.get_stats().register_counter(f"pkts_failed")
        self.get_stats().register_cycle_map(f"{self.get_node_id()}")
        self.get_stats().register_interval_counter(f"pkts_sent_interval_{self.get_node_id()}", interval = 5)

    def advance(self, cycle):
        """
        @brief      Generates packets every cycle and attempts to send it.
        @param      cycle - an integer representing current simulation time.
        """
        self.get_stats().record_cycle(f"{self.get_node_id()}", cycle, False)

        # if self.get_node_id() == "A1" or self.get_node_id() == "A2":
            # return

        if self.get_node_id() == "A0":
            stream_rate = 1
        elif self.get_node_id() == "A1":
            stream_rate = 2
        elif self.get_node_id() == "A2":
            stream_rate = 4
        else:
            return

        if cycle % stream_rate != 0:
            return

        output_port = self.get_node_id() + '_out'

        pkt_id = self.get_node_id() + "_" + str(cycle)
        data = "__" + self.get_node_id() + "___" + str(cycle)
        packet = Packet(pkt_id, data)

        if self.send_pkt(packet, output_port, cycle) < 0:
            logger.warning(f"{self.get_node_id()} unable to send packet {pkt_id}")
            self.incr_counter(f"pkts_failed", 1)
        else:
            logger.info(f"{self.get_node_id()} sent packet {pkt_id}")
            self.incr_counter(f"pkts_sent", 1)
            self.record_cycle(f"{self.get_node_id()}", cycle, True)
            self.get_stats().incr_interval_counter(f"pkts_sent_interval_{self.get_node_id()}", cycle)

    def teardown(self):
        logger.info(f"Node {self.get_node_id()} stats:")
        self.get_stats().dump_summary()
        logger.info(f"\n")