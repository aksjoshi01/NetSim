"""
@file       switch.py
@brief      A simple switch node with 3 input ports and 1 output port that performs round-robin arbitration.
"""

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
        self.log = {}

    def advance(self, cycle):
        """
        @brief      This method performs a round-robin scheduling scheme to determine which
                    input port must be selected to forward the packet from.
        @param      cycle - an integer representing current simulation time
        """
        input_ports = list(self.get_input_ports().values())
        output_ports = list(self.get_output_ports().values())

        self.log[cycle] = False

        if not output_ports:
            return

        output_port = output_ports[0]
        num_inputs = len(input_ports)
        if num_inputs == 0:
            return

        # Round-robin over input ports
        for i in range(num_inputs):
            port_idx = (self.rr_index + i) % num_inputs
            input_port = input_ports[port_idx]
            pkt = input_port.recv_pkt(cycle)
            if pkt:
                output_port.send_pkt(pkt, cycle)
                print(f"Switch forwarded packet {pkt.get_pkt_id()} from {input_port.get_port_id()} to {output_port.get_port_id()}")
                self.rr_index = (port_idx + 1) % num_inputs
                self.pkts_forwarded += 1
                self.log[cycle] = True
                break

    def get_stats(self):
        """
        @brief      Prints the total packets forwarded and generates a per-cycle plot.
        """
        print(f"Switch {self.get_node_id()} forwarded a total of {self.pkts_forwarded} packets")
        plotter = Plotter(self.log, self.get_node_id())
        plotter.plot_graph("Forward")