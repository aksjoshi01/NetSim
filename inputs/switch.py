"""
@file       switch.py
@brief      A switch node with round-robin arbitration.
"""

from collections import deque
import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet
from port import InputPort, OutputPort

class Switch(Node):
    """
    @class      Switch
    """
    def __init__(self):
        """
        @brief      A constructor for the Switch class.
        """
        super().__init__()
        self.__rr_index = 0
        self.__processing_latency = 2
        self.__pipeline = deque()
    
    def get_rr_index(self):
        return self.__rr_index

    def set_rr_index(self, rr_index):
        self.__rr_index = rr_index

    def get_pipeline(self):
        return self.__pipeline

    def get_processing_latency(self):
        return self.__processing_latency

    def initialize(self):
        self.get_stats().register_counter(f"pkts_forwarded")
        self.get_stats().register_cycle_map(f"{self.get_node_id()}")

    def advance(self, cycle):
        """
        @brief      This method performs a round-robin scheduling scheme to determine which
                    input port to select the packet to be forwarded.
        @param      cycle - an integer representing current simulation time
        """
        self.get_stats().record_cycle(f"{self.get_node_id()}", cycle, False)

        input_ports = list(self.get_input_ports().values())
        num_inputs = len(input_ports)
        if num_inputs == 0:
            return

        output_ports = self.get_output_ports()
        output_port = next(iter(output_ports.values()))

        # Round-robin over input ports
        for i in range(num_inputs):
            if output_port.get_credit() == 0:
                break

            port_idx = (self.get_rr_index() + i) % num_inputs
            input_port = input_ports[port_idx]
            pkt = self.recv_pkt(input_port.get_port_id(), cycle)
            if pkt:
                logger.info(f"Switch received packet {pkt.get_pkt_id()} from {input_port.get_port_id()}")
                ready_cycle = cycle + self.get_processing_latency()
                self.get_pipeline().append((ready_cycle, pkt, input_port.get_port_id()))
                self.set_rr_index((port_idx + 1) % num_inputs)
                break

        # Check if packets in the pipeline is ready to be forwarded
        if self.get_pipeline():
            ready_cycle, pkt, input_port_id = self.get_pipeline()[0]
            if ready_cycle == cycle:
                val = self.send_pkt(pkt, output_port.get_port_id(), cycle) 
                if val == 0:
                    logger.info(f"Switch forwarded packet {pkt.get_pkt_id()} from {input_port_id} to {output_port.get_port_id()}")
                    self.get_pipeline().popleft()
                    self.incr_counter(f"pkts_forwarded", 1)
                    self.record_cycle(f"{self.get_node_id()}", cycle, True)
                else:
                    logger.error(f"Switch unable to send packet {pkt.get_pkt_id()} - error code: {val}")

    def finalize(self):
        logger.info(f"Node {self.get_node_id()} stats:")
        self.get_stats().dump_summary()
        logger.info(f"\n")