from collections import deque
import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet
from port import InputPort, OutputPort

class NewSwitch(Node):
    def __init__(self, algorithm = "fifo"):
        super().__init__()
        self.processing_latency = 2
        self.routing_table = {}
        self.sched_queues = {}

        # map available algorithms to their functions
        # currently only FIFO is implemented
        self.algo_map = {
            "fifo": self.fifo_algorithm
        }
        if algorithm not in self.algo_map:
            raise ValueError(f"Unknown scheduling algorithm: {algorithm}")
        self.algo_fn = self.algo_map[algorithm]

    def setup(self):
        # construct the routing table
        self.routing_table["B0"] = "S0_out"
        self.routing_table["B1"] = "S1_out"
        
        # initialize the scheduling queues for all output ports
        for out_id in ['S0_out', 'S1_out']:
            self.sched_queues[out_id] = deque()

        # register stats
        self.register_counter_stats(f"pkts_forwarded")
        self.register_cycle_stats(f"{self.get_node_id()}")
        self.register_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", interval=1)

    def advance(self, cycle):
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)

        # step 1: service/grant the existing inputs in the scheduling queues
        for out_id in self.sched_queues.keys():
            self.algo_fn(out_id, cycle)

        # step 2: add current inputs to scheduling queues
        for in_id in ['S0_in', 'S1_in', 'S2_in']:
            input_port = self.get_input_port(in_id)
            if not input_port:
                continue
            pkt = input_port.peek()
            if pkt:
                out_id = self.routing_table[pkt.get_dst_node_id()]
                ready_cycle = cycle + self.processing_latency
                if not self.sched_queues[out_id] or self.sched_queues[out_id][-1][0] == ready_cycle:
                    self.sched_queues[out_id].append((ready_cycle, pkt, in_id))
                    logger.debug(f"Switch received packet {pkt.get_pkt_id()} from {in_id} and queued for {out_id}")

    # ---------------------
    # Scheduling algorithms
    # ---------------------
    def fifo_algorithm(self, out_id, cycle):
        """Serve packets in FIFO order."""
        if not self.sched_queues[out_id]:
            return
        if self.get_output_port(out_id).get_credit() <= 0:
            return

        ready_cycle, pkt, in_id = self.sched_queues[out_id][0]
        if ready_cycle > cycle:
            return

        # dequeue and send
        self.sched_queues[out_id].popleft()
        self.recv_pkt(in_id, cycle)
        self.send_pkt(pkt, out_id, cycle)

        logger.debug(f"Switch forwarded packet {pkt.get_pkt_id()} from {in_id} to {out_id}")
        self.incr_counter_stats("pkts_forwarded", 1)
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)
        self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_forwarded"))

