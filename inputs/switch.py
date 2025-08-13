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
        self.__processing_latency = 0
        self.__pipeline = deque()
    
    def get_rr_index(self):
        return self.__rr_index

    def set_rr_index(self, rr_index):
        self.__rr_index = rr_index

    def get_pipeline(self):
        return self.__pipeline

    def get_processing_latency(self):
        return self.__processing_latency

    def setup(self):
        self.register_counter_stats(f"pkts_forwarded")
        self.register_cycle_stats(f"{self.get_node_id()}")
        self.register_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", interval = 1)

    def advance(self, cycle):
        """
        @brief      This method performs a round-robin scheduling scheme to determine which
                    input port to select the packet to be forwarded.
        @param      cycle - an integer representing current simulation time
        """
        self.record_cycle_stats(f"{self.get_node_id()}", cycle, False)
        input_ports = ['S0_in', 'S1_in', 'S2_in']
        output_port = 'S_out'

        num_inputs = len(input_ports)

        # Round-robin over input ports
        for i in range(num_inputs):
            if self.get_output_port(output_port).get_credit() == 0:
                break

            port_idx = (self.get_rr_index() + i) % num_inputs
            input_port = self.get_input_port(input_ports[port_idx])
            pkt = self.recv_pkt(input_port.get_port_id(), cycle)
            if pkt:
                logger.debug(f"Switch received packet {pkt.get_pkt_id()} from {input_port.get_port_id()}")
                ready_cycle = cycle + self.get_processing_latency()
                self.get_pipeline().append((ready_cycle, pkt, input_port.get_port_id()))
                self.set_rr_index((port_idx + 1) % num_inputs)
                break

        # Check if packets in the pipeline is ready to be forwarded
        if self.get_pipeline():
            ready_cycle, pkt, input_port_id = self.get_pipeline()[0]
            if ready_cycle == cycle:
                val = self.send_pkt(pkt, output_port, cycle)
                if val == 0:
                    logger.debug(f"Switch forwarded packet {pkt.get_pkt_id()} from {input_port_id} to {output_port}")
                    self.get_pipeline().popleft()
                    self.incr_counter_stats(f"pkts_forwarded", 1)
                    self.record_cycle_stats(f"{self.get_node_id()}", cycle, True)
                    self.incr_interval_counter_stats(f"{self.get_node_id()}_cumulative_pkts", cycle, self.get_stats().get_counter("pkts_forwarded"))
                else:
                    logger.error(f"Switch unable to send packet {pkt.get_pkt_id()}")
