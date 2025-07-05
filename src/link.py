"""
@file       link.py
@brief      A link logically connects two ports.
            Source is the OutputPort of one node.
            Destination is the InputPort of another node.
@author     Akshay Joshi
"""


from collections import deque
from typing import Optional

from packet import Packet


class Link:
    """
    @brief      Consists of data members like the source port, destination port, latency of the link and link ID.
    """
    def __init__(self, link_id: str, src: 'OutputPort', dst: 'InputPort', latency: int):
        self.link_id = link_id
        self.src = src
        self.dst = dst
        self.latency = latency
        self.fifo: deque[Optional[Packet]] = deque([None] * latency)
        
    
    def add_src(self, src: 'OutputPort'):
        """
        @brief      Add a source port to the link.
        @param      src - The source port to be added.
        """
        self.src = src


    def add_dst(self, dst: 'InputPort'):
        """
        @brief      Add a destination port to the link.
        @param      dest - The destination port to be added.  
        """
        self.dst = dst


    def send_pkt(self, pkt: 'Packet'):
        """
        @brief      Insert pkt at the end of the fifo
        @param      pkt to be sent over the link
        """
        if self.fifo[-1] is None:
            self.fifo[-1] = pkt
            return True
        else:
            return False


    def advance(self, current_cycle: int):
        """
        @brief      Simulate the forwarding of packet over the link. The fifo is initially filled with None values.
                    We simulate the advancing of the packet by popping the pkt from the left of the fifo.
                    If the popped pkt is not None, then we know that the packet has reached its 
                    destination. This is possible because the initial fifo size is equal to the latency 
                    of the link.
        """
        arriving_pkt = self.fifo.popleft()
        if arriving_pkt:
            self.dst.recv_pkt(arriving_pkt)

        self.fifo.append(None)