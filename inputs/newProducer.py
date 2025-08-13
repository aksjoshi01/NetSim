import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet

class NewProducer(Node):
    def __init__(self):
        super().__init__()
        
    def setup(self):
        self.register_counter_stats(f"pkts_sent")
        self.register_counter_stats(f"pkts_failed")
        self.register_cycle_stats(f"{self.get_node_id()}")
        self.register_interval_counter_stats(f"pkts_sent_interval_{self.get_node_id()}", interval = 5)
        self.register_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", interval = 1)

    def advance(self, cycle):
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)

        pkt_id = self.get_node_id() + "_" + str(cycle)
        output_port = self.get_node_id() + "_out"

        # Packet generation logic customized based on node_id
        if self.get_node_id() == "A0":
            if cycle % 2 == 0:
                packet = Packet(pkt_id, "B0")
            else:
                packet = Packet(pkt_id, "B1")
        elif self.get_node_id() == "A1":
            if cycle % 2 == 0:
                packet = Packet(pkt_id, "B1")
            else:
                packet = Packet(pkt_id, "B0")
        elif self.get_node_id() == "A2":
            if cycle % 2 == 0:
                packet = Packet(pkt_id, "B0")
            else:
                packet = Packet(pkt_id, "B1")

        if self.send_pkt(packet, output_port, cycle) < 0:
            logger.warning(f"{self.get_node_id()} unable to send packet {pkt_id}")

            # record failure stats
            self.incr_counter_stats(f"pkts_failed", 1)
            self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_sent"))
        else:
            logger.debug(f"{self.get_node_id()} sent packet {pkt_id}")
            
            # record success stats
            self.incr_counter_stats(f"pkts_sent", 1)
            self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)
            self.incr_interval_counter_stats(f"pkts_sent_interval_{self.get_node_id()}", cycle, 1)
            self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_sent"))
