"""
@file       node.py
@brief      Node represents an entity in the network that can communicate with other entities.
@author     Akshay Joshi
"""


from collections import deque
from typing import Dict, List, Optional
from abc import abstractmethod

from port import OutputPort, InputPort
from packet import Packet


class Node:
    """
    @class      Node
    @brief      A simple network node that can send and receive packets. The node has input and output ports, 
                and can process packets in its input queue.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.input_ports: Dict[str, 'InputPort'] = {}
        self.output_ports: Dict[str, 'OutputPort'] = {}
        self.recvd_pkts: deque[Packet] = deque()


    def add_input_port(self, node_id: str, link: 'Link', fifo_capacity: int):
        """
        @brief      Add new input port to recv pkts from node `node_id`
        @param      node_id
                    link - the connected link between the input port and the output port
                    fifo_capacity - size of the fifo
        """
        self.input_ports[node_id] = InputPort(self, link, fifo_capacity)


    def add_output_port(self, node_id: str, link: 'Link', dst_fifo_capacity: int):
        """
        @brief      Add new output port to send pkts to node `node_id`
        @param      node_id
                    link - the connected link between the output port and the input port
                    dst_fifo_capacity - fifo size of the destination node's
        """
        self.output_ports[node_id] = OutputPort(self, link, dst_fifo_capacity)


    def get_output_port(self, node_id: str):
        """
        @brief      Returns the output port instance for the specified node
        @param      node_id - Returns the output port associated with the node `node_id`
        """
        return self.output_ports[node_id]


    def get_input_port(self, node_id: str):
        """
        @brief      Returns the input port instance for the specified node
        @param      node_id - Returns the input port associated with the node `node_id`
        """
        return self.input_ports[node_id]


    def send_pkt(self, pkt: 'Packet'):
        """
        @brief      Forwards the packet to its OutputPort.
        @param      pkt - Packet instance to be sent
        """
        if self.output_ports:
            dst_output_port = self.output_ports.get(pkt.dst)
            if dst_output_port:
                dst_output_port.pending_sends.append(pkt)
            else:
                print(f"Node {self.node_id} has no output port for packet {pkt}")


    def recv_pkt(self):
        """
        @brief      Receive the packets present in the input ports
        """
        for key, input_port in self.input_ports.items():
            if input_port.fifo:
                pkt = input_port.fifo.popleft()
                self.recvd_pkts.append(pkt)

                # if the recvd pkt is a regular pkt, then we need to send an ACK back to the node
                if pkt.is_ack == False:
                    ack_pkt_id = "ACK_" + pkt.pkt_id
                    ack_pkt = Packet(pkt_id = ack_pkt_id, src = self.node_id, dst = key, size = 8, cycle = -1, is_ack = True)
                    self.output_ports[key].pending_sends.append(ack_pkt)
                else:
                    self.output_ports[key].dst_fifo_capacity += 1
        

    @abstractmethod
    def process_pkt(self, pkt: 'Packet'):
        pass


    @abstractmethod
    def advance(self, current_cycle: int):
        pass
        
