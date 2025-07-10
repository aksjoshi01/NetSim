"""
@file       producer.py
@brief      A producer node that generates a packet every cycle and sends it to its output port.
"""

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
        output_ports = self.get_output_ports()
        if not output_ports:
            self.log[cycle] = False
            return

        pkt_id = self.get_node_id() + "_" + str(cycle)
        data = "__" + self.get_node_id() + "___" + str(cycle)
        packet = Packet(pkt_id, data)
        
        output_port = next(iter(output_ports.values()))
        # output_port = list(output_ports.values())[0]
        if output_port.send_pkt(packet, cycle) < 0:
            print(f"{self.get_node_id()} unable to send packet {pkt_id}")
            self.log[cycle] = False
        else:
            print(f"{self.get_node_id()} sent packet {pkt_id}")
            self.pkts_sent += 1
            self.log[cycle] = True

    def get_stats(self):
        """
        @brief      Prints the total packets sent and generates a per-cycle plot.
        """
        print(f"Producer {self.get_node_id()} sent a total of {self.pkts_sent} packets")
        plotter = Plotter(self.log, self.get_node_id())
        plotter.plot_graph("Send")