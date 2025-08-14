from collections import deque
import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet
from port import InputPort, OutputPort

class Switch(Node):
    def __init__(self, algorithm="fifo"):
        super().__init__()
        self.processing_latency = 1
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
        self.routing_table["S1"] = {'B0': 'S1_0_out', 'B1': 'S1_1_out', 'B2': 'S1_0_out', 'B3': 'S1_1_out'}
        self.routing_table["S2"] = {'B0': 'S2_0_out', 'B1': 'S2_1_out', 'B2': 'S2_0_out', 'B3': 'S2_1_out'}
        self.routing_table["S3"] = {'B0': 'S3_0_out', 'B1': 'S3_0_out', 'B2': 'S3_1_out', 'B3': 'S1_1_out'}
        self.routing_table["S4"] = {'B0': 'S4_0_out', 'B1': 'S4_0_out', 'B2': 'S4_1_out', 'B3': 'S4_1_out'}
        self.routing_table["S5"] = {'B0': 'S5_0_out', 'B1': 'S5_1_out'}
        self.routing_table["S6"] = {'B2': 'S6_0_out', 'B3': 'S6_1_out'}
        
        # initialize the scheduling queues for all output ports
        for out_id in self.get_output_port_ids():
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
        for in_id in self.get_input_port_ids():
            input_port = self.get_input_port(in_id)
            if not input_port:
                continue
            # peek at the packet in the input port
            pkt = input_port.peek()
            if pkt:
                # check the dest node id and add to the tail of the appropriate scheduling queue
                out_id = self.routing_table[self.get_node_id()][pkt.get_dst_node_id()]
                ready_cycle = cycle + self.processing_latency
                # if the scheduling queue is empty or the last packet in the queue will be sent at the same cycle,
                # append the new packet to the queue
                # this means that at any point in time, the scheduling queue will have packets that are ready to be sent at the same cycle
                if not self.sched_queues[out_id] or self.sched_queues[out_id][-1][0] == ready_cycle:
                    self.sched_queues[out_id].append((ready_cycle, pkt, in_id))
                    logger.debug(f"Switch received packet {pkt.get_pkt_id()} from {in_id} and queued for {out_id}")

    # ------------------------------------------
    # Scheduling algorithms
    # ------------------------------------------
    def fifo_algorithm(self, out_id, cycle):
        # check if there are packets to process and if the output port has credits
        if not self.sched_queues[out_id]:
            return
        if self.get_output_port(out_id).get_credit() <= 0:
            return

        # check if the first packet in the queue is ready to be sent
        ready_cycle, pkt, in_id = self.sched_queues[out_id][0]
        if ready_cycle > cycle:
            return

        # dequeue the packet and send it
        self.sched_queues[out_id].popleft()
        self.recv_pkt(in_id, cycle)
        self.send_pkt(pkt, out_id, cycle)

        # record the stats
        logger.debug(f"Switch forwarded packet {pkt.get_pkt_id()} from {in_id} to {out_id}")
        self.incr_counter_stats("pkts_forwarded", 1)
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)
        self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_forwarded"))

