"""
@file      packet.py
@brief     Contains the Packet and CreditPacket class.
@author    Akshay Joshi
"""

class Packet:
    """
    @class      Packet
    """
    def __init__(self, pkt_id: str, data):
        """
        @brief      A constructor for the Packet class.
        @param      pkt_id - a string representing ID of the packet
        @param      data - user data that must be included in the packet
        """
        self.__pkt_id = pkt_id
        self.__data = data

    def get_pkt_id(self):
        """
        @brief      Returns the ID of the packet.
        @return     pkt_id - a string representing ID of the packet.
        """
        return self.__pkt_id

    def get_data(self):
        """
        @brief      Returns the data in the packet.
        @return     data - user data present in the packet.
        """
        return self.__data

class CreditPacket:
    """
    @class      CreditPacket
    @brief      Represents the credit packet that is sent as an 
                acknowledgement when a packet is received.
    """
    pass