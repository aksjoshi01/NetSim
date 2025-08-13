import logging
logger = logging.getLogger(__name__)

from node import Node

class NewConsumer(Node):
    def __init__(self):
        super().__init__()
        self.rate = 4

    def setup(self):
        self.register_counter_stats(f"pkts_recvd")
        self.register_cycle_stats(f"{self.get_node_id()}")

    def advance(self, cycle):
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)
        input_port = self.get_node_id() + "_in"

        pkt = self.recv_pkt(input_port, cycle)
        if pkt:
            logger.debug(f"{self.get_node_id()} received packet {pkt.get_pkt_id()} on {input_port}")
            self.incr_counter_stats(f"pkts_recvd", 1)
            self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)