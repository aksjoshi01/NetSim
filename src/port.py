"""
@file       port.py
@brief      Port is used to communicate with other nodes.
            InputPort is where the node receives packets. 
            OutputPort is where the node sends packets.
@author     Akshay Joshi
"""


from collections import deque
from typing import List

from link import Link
from packet import Packet


class Port:
    """
    @brief      A base class for network ports. It represents a port in a network node that can be connected to a link.
    """
    def __init__(self, parent_node: 'Node', connected_link: 'Link'):
        self.parent_node = parent_node
        self.connected_link = connected_link


class InputPort(Port):
    """
    @brief      A class representing an input port in a network node. It can receive packets and store them in a FIFO.
    """
    def __init__(self, parent_node: 'Node', connected_link: 'Link', fifo_capacity: int):
        super().__init__(parent_node, connected_link)
        self.fifo_capacity = fifo_capacity
        self.fifo: deque[Packet] = deque()


    def recv_pkt(self, pkt: 'Packet'):
        """
        @brief      Receive pkt into this input port's fifo
        @param      pkt that is received by the input port
        """
        if len(self.fifo) < self.fifo_capacity:
            self.fifo.append(pkt)
            print(f"[+] Node {pkt.dst} received pkt {pkt.pkt_id} from Node {pkt.src}")
        else:
            print(f"[*] Node {pkt.dst} did not recv pkt {pkt.pkt_id} from Node {pkt.src}")


class OutputPort(Port):
    """
    @brief      A class representing an output port in a network node. It can send packets to the connected link.
    """
    def __init__(self, parent_node: 'Node',connected_link: 'Link', dst_fifo_capacity: int):
        super().__init__(parent_node, connected_link)
        self.dst_fifo_capacity = dst_fifo_capacity
        self.pending_sends: deque[Packet] = deque()


    def send_pkt(self):
        """
        @brief      Forward the packet from the port onto the link
        """
        if self.pending_sends:
            if self.dst_fifo_capacity > 0:
                pkt = self.pending_sends.popleft()
                self.connected_link.send_pkt(pkt)
                if pkt.is_ack == False:
                    self.dst_fifo_capacity -= 1
                print(f"[-] Node {pkt.src} sent pkt {pkt.pkt_id} to Node {pkt.dst}")
            else:
                print(f"[*] Node {self.parent_node.node_id} unable to send pkt")
                