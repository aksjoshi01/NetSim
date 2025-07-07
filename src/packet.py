"""
@file      packet.py
@author    Akshay Joshi
"""

class Packet:
    def __init__(self, pkt_id: str, message: str):
        self.__pkt_id = pkt_id
        self.__message = message

    def get_pkt_id(self):
        return self.__pkt_id