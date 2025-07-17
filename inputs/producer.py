"""
@file       producer.py
@brief      A producer node that generates a packet every cycle and sends it to its output port.
"""

import logging
logger = logging.getLogger(__name__)

from node import Node
from packet import Packet
from plotter import Plotter

class Producer(Node):
    """
    @class      Producer
    """
    def __init__(self):
        """
        @brief      A constructor for the Producer class
        """
        super().__init__()
        self.pkts_sent = 0

    def advance(self, cycle):
        """
        @brief      Generates packets every cycle and attempts to send it.
        @param      cycle - an integer representing current simulation time.
        """

        self.stats.log_node_activity(self.get_node_id(), cycle, False)

        # if self.get_node_id() == "A1" or self.get_node_id() == "A2":
        #     return

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

        output_ports = self.get_output_ports()
        if not output_ports:
            return

        pkt_id = self.get_node_id() + "_" + str(self.pkts_sent)
        data = "__" + self.get_node_id() + "___" + str(cycle)
        packet = Packet(pkt_id, data)

        output_port = next(iter(output_ports.values()))
        if output_port.send_pkt(packet, cycle) < 0:
            logger.warning(f"{self.get_node_id()} unable to send packet {pkt_id}")
        else:
            logger.info(f"{self.get_node_id()} sent packet {pkt_id} => curr_credit = {output_port.get_credit()}")
            self.pkts_sent += 1
            self.stats.log_node_activity(self.get_node_id(), cycle, True)
            self.stats.increment_pkt_sent(self.get_node_id())