"""
@file      packet.py
@author    Akshay Joshi
"""

class Packet:
    def __init__(self, pkt_id: str, message: str):
        self.pkt_id = pkt_id
        self.message = message