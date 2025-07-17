"""
@file       switch.py
@brief      A simple switch node with 3 input ports and 1 output port that performs round-robin arbitration.
"""

from collections import deque
import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet
from port import InputPort, OutputPort
from plotter import Plotter

class Switch(Node):
    """
    @class      Switch
    """
    def __init__(self):
        """
        @brief      A constructor for the Switch class.
        """
        super().__init__()
        self.rr_index = 0
        self.pkts_forwarded = 0
        self.processing_latency = 2
        self.pipeline = deque()

    def advance(self, cycle):
        """
        @brief      This method performs a round-robin scheduling scheme to determine which
                    input port to select the packet to be forwarded.
        @param      cycle - an integer representing current simulation time
        """
        input_ports = list(self.get_input_ports().values())
        output_ports = list(self.get_output_ports().values())

        self.stats.log_node_activity(self.get_node_id(), cycle, False)

        if not output_ports:
            return

        output_port = output_ports[0]
        num_inputs = len(input_ports)
        if num_inputs == 0:
            return

        # Check if packets in the pipeline is ready to be forwarded
        if self.pipeline:
            ready_cycle, pkt, input_port_id = self.pipeline[0]
            if ready_cycle == cycle:
                self.pipeline.popleft()
                if output_port.send_pkt(pkt, cycle) == 0:
                    logger.info(f"Switch forwarded packet {pkt.get_pkt_id()} from {input_port_id} to {output_port.get_port_id()}")
                    self.pkts_forwarded += 1
                    self.stats.log_node_activity(self.get_node_id(), cycle, True)
                    self.stats.increment_pkt_sent(self.get_node_id())
                else:
                    logger.error(f"Switch unable to send packet {pkt.get_pkt_id()}")                   

        # Round-robin over input ports
        for i in range(num_inputs):
            port_idx = (self.rr_index + i) % num_inputs
            input_port = input_ports[port_idx]
            pkt = input_port.recv_pkt(cycle)
            if pkt:
                logger.info(f"Switch received packet {pkt.get_pkt_id()} from {input_port.get_port_id()}")
                self.stats.increment_pkt_recvd(self.get_node_id())
                ready_cycle = cycle + self.processing_latency
                self.pipeline.append((ready_cycle, pkt, input_port.get_port_id()))
                self.rr_index = (port_idx + 1) % num_inputs
                break