"""
@file       link.py
@brief      Implements the Link class that models connections between nodes.
@author     Akshay Joshi
"""

from collections import deque
from typing import Optional

from packet import Packet, CreditPacket

class Link:
    """
    @class      Link
    """
    def __init__(self):
        """
        @brief      A constructor for the Link class that initialises the attributes
                    to None.
        """
        self.__link_id = None
        self.__output_port = None
        self.__input_port = None
        self.__latency = None
        self.__pipeline = None
        self.__credit_pipeline = None
        self.__cycle = -1
        self.stats = None

    def set_stats(self, stats):
        self.stats = stats

    def set_link_id(self, link_id):
        """
        @brief      Assigns link_id to the Link object.
        @param      link_id - unique id of the Link object.
        """
        assert isinstance(link_id, str), "Error: link_id should be a string"
        self.__link_id = link_id

    def set_latency(self, latency):
        """
        @brief      Sets the latency value, if and only if it is a positive integer.
        @param      latency - an integer value representing the link latency.
        """
        assert isinstance(latency, int), "Error: latency should be a positive integer"
        assert latency > 0, "Error: latency should be greater than zero"
        self.__latency = latency

    def set_output_port(self, output_port: 'OutputPort'):
        """
        @brief      Sets the Output port of the Link.
        @param      output_port - OutputPort object representing one end of the link.
        """
        assert output_port is not None, "Error: output port should not be None"
        self.__output_port = output_port

    def set_input_port(self, input_port: 'InputPort'):
        """
        @brief      Sets the Input port of the Link.
        @param      input_port - InputPort object representing one end of the link.
        """
        assert input_port is not None, "Error: input port should not be None"
        self.__input_port = input_port
    
    def init_fifos(self):
        """
        @brief      Initialises the pipelines needed for carrying packets.
        """
        self.__pipeline = deque(maxlen = self.__latency)
        self.__credit_pipeline = deque(maxlen = self.__latency)

    def get_link_id(self):
        """
        @brief      Returns the link_id of the Link.
        @return     a string representing ID of the Link.
        """
        return self.__link_id

    def get_latency(self):
        """
        @brief      Returns the link latency.
        @return     an integer value representing latency of the link.
        """
        return self.__latency

    def send_pkt(self, pkt: 'Packet', current_cycle: int):
        """
        @brief      Appends the packet to its pipeline if there is space.
        @param      pkt - Packet object to be sent.
        @param      current_cycle - integer value representing the simulation time.
        @return     0 on success, -1 otherwise.
        """
        assert pkt is not None, "Error: packet cannot be None"
        assert isinstance(pkt, Packet), "Error: pkt should be of class type Packet"

        if len(self.__pipeline) < self.__latency:
            data = [pkt, current_cycle]
            self.__pipeline.append(data)
            return 0

        return -1

    def send_credit(self, credit_pkt: 'CreditPacket', current_cycle: int):
        """
        @brief      Appends the credit packet to its pipeline if there is space.
        @param      credit_pkt - CreditPacket to be sent.
        @param      current_cycle - integer value representing the simulation time.
        @return     0 on success, -1 otherwise.
        """
        if len(self.__credit_pipeline) < self.__latency:
            data = [credit_pkt, current_cycle]
            self.__credit_pipeline.append(data)
            return 0

        return -1

    def advance(self, current_cycle: int):
        """
        @brief      Advances the packets in the pipeline.
        @param      current_cycle - integer value representing the simulation time.
        """

        self.stats.link_transmit(self.__link_id, active = False)

        if len(self.__pipeline) > 0 or len(self.__credit_pipeline) > 0:
            self.stats.link_transmit(self.__link_id, active = True)
            self.stats.record_link_active(self.__link_id)
    
        # Advance the packets
        if len(self.__pipeline) > 0:
            pkt = self.__pipeline[0]
            if pkt[1] + self.__latency == current_cycle:
                self.__pipeline.popleft()
                self.__input_port.recv_from_link(pkt[0])

        # Advance the credits
        if len(self.__credit_pipeline) > 0:
            credit_pkt = self.__credit_pipeline[0]
            if credit_pkt[1] + self.__latency == current_cycle:
                self.__credit_pipeline.popleft()
                self.__output_port.increment_credit()