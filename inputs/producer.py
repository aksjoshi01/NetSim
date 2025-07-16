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
        self.log = {}

    def advance(self, cycle):
        """
        @brief      Generates packets every cycle and attempts to send it.
        @param      cycle - an integer representing current simulation time.
        """

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
            self.log[cycle] = False
            return

        pkt_id = self.get_node_id() + "_" + str(self.pkts_sent)
        data = "__" + self.get_node_id() + "___" + str(cycle)
        packet = Packet(pkt_id, data)

        output_port = next(iter(output_ports.values()))
        if output_port.send_pkt(packet, cycle) < 0:
            logger.warning(f"{self.get_node_id()} unable to send packet {pkt_id}")
            self.log[cycle] = False
        else:
            logger.info(f"{self.get_node_id()} sent packet {pkt_id} => curr_credit = {output_port.get_credit()}")
            self.pkts_sent += 1
            self.log[cycle] = True

    def get_stats(self):
        """
        @brief      Prints the total packets sent and generates a per-cycle plot.
        """
        logger.info(f"Producer {self.get_node_id()} sent a total of {self.pkts_sent} packets")
        plotter = Plotter(self.log, self.get_node_id())
        plotter.plot_graph("Send")