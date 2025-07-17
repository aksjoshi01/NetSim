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
        self.processing_latency = 2
        self.pipeline = deque()

    def advance(self, cycle):
        """
        @brief      This method performs a round-robin scheduling scheme to determine which
                    input port to select the packet to be forwarded.
        @param      cycle - an integer representing current simulation time
        """
        input_ports = list(self.get_input_ports().values())
        num_inputs = len(input_ports)
        if num_inputs == 0:
            return
               
        # Round-robin over input ports
        for i in range(num_inputs):
            port_idx = (self.rr_index + i) % num_inputs
            input_port = input_ports[port_idx]
            pkt = self.recv_pkt(input_port.get_port_id(), cycle)
            if pkt:
                logger.info(f"Switch received packet {pkt.get_pkt_id()} from {input_port.get_port_id()}")
                ready_cycle = cycle + self.processing_latency
                self.pipeline.append((ready_cycle, pkt, input_port.get_port_id()))
                self.rr_index = (port_idx + 1) % num_inputs
                break

        output_ports = self.get_output_ports()
        output_port = next(iter(output_ports.values()))

        # Check if packets in the pipeline is ready to be forwarded
        if self.pipeline:
            ready_cycle, pkt, input_port_id = self.pipeline[0]
            if ready_cycle == cycle:
                self.pipeline.popleft()
                if self.send_pkt(pkt, output_port.get_port_id(), cycle) == 0:
                    logger.info(f"Switch forwarded packet {pkt.get_pkt_id()} from {input_port_id} to {output_port.get_port_id()}")
                else:
                    logger.error(f"Switch unable to send packet {pkt.get_pkt_id()}")                   