"""
@file      packet.py
@brief     Packet represents a bag of information.
@author    Akshay Joshi
"""


class Packet:
    """
    @brief      A class representing a network packet. It contains information about the packet's ID, source, destination, size, and cycle.
    """
    def __init__(self, pkt_id: str, src: str, dst: str, size: int, cycle: int, is_ack: bool = False):
        self.pkt_id = pkt_id
        self.src = src
        self.dst = dst
        self.size = size
        self.cycle = cycle
        self.is_ack = is_ack