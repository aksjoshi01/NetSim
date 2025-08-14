import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet

class Producer(Node):
    def __init__(self):
        super().__init__()
        self.pattern = None
        self.pattern_params = []
        self.pattern_index = 0

    def set_pattern(self, pattern, params):
        self.pattern = pattern
        if params:
            self.pattern_params = params.split(":")
        else:
            self.pattern_params = []

    def setup(self):
        # register the necessary stats
        self.register_counter_stats(f"pkts_sent")
        self.register_counter_stats(f"pkts_failed")
        self.register_cycle_stats(f"{self.get_node_id()}")
        self.register_interval_counter_stats(f"pkts_sent_interval_{self.get_node_id()}", interval = 5)
        self.register_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", interval = 1)

    def advance(self, cycle):
        # record the current cycle stat as not having sent a packet
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)

        # pattern-driven packet generation
        if self.pattern == "alternate" and self.pattern_params:
            dst_id = self.pattern_params[self.pattern_index]
            self.pattern_index = (self.pattern_index + 1) % len(self.pattern_params)
        else:
            return

        pkt_id = f"{self.get_node_id()}_{cycle}"
        packet = Packet(pkt_id, dst_id)
        output_port = f"{self.get_node_id()}_out"

        # attempt to send the packet and record the stats
        if self.send_pkt(packet, output_port, cycle) < 0:
            logger.warning(f"{self.get_node_id()} unable to send packet {pkt_id}")
            self.incr_counter_stats(f"pkts_failed", 1)
            self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_sent"))
        else:
            logger.debug(f"{self.get_node_id()} sent packet {pkt_id}")
            self.incr_counter_stats(f"pkts_sent", 1)
            self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)
            self.incr_interval_counter_stats(f"pkts_sent_interval_{self.get_node_id()}", cycle, 1)
            self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_sent"))
