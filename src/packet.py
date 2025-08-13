"""
@file      packet.py
@brief     Contains the Packet and CreditPacket class.
@author    Akshay Joshi
"""

class Packet:
    """
    @class      Packet
    """
    def __init__(self, pkt_id, dst_node_id):
        """
        @brief      A constructor for the Packet class.
        @param      pkt_id - a string representing ID of the packet
        """
        self.__pkt_id = pkt_id
        self.__dst_node_id = dst_node_id

    def get_pkt_id(self):
        """
        @brief      Returns the ID of the packet.
        @return     pkt_id - a string representing ID of the packet.
        """
        return self.__pkt_id

    def get_dst_node_id(self):
        """
        @brief      Returns the destination node ID of the packet.
        @return     dst_node_id - a string representing ID of the destination node.
        """
        return self.__dst_node_id

class CreditPacket:
    """
    @class      CreditPacket
    @brief      Represents the credit packet that is sent as an 
                acknowledgement when a packet is received.
    """