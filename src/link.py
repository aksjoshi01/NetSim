"""
@file       link.py
@brief      Implements the Link class that models connections between nodes.
@author     Akshay Joshi
"""

import logging
logger = logging.getLogger(__name__)

from collections import deque
from typing import Optional

from packet import Packet, CreditPacket

class Link:
    """
    @class      Link
    """
    def __init__(self, link_id, latency):
        """
        @brief      A constructor for the Link class that initialises the attributes
                    to None.
        """
        assert isinstance(link_id, str), "Error: link_id should be a string"
        assert isinstance(latency, int), "Error: latency should be a positive integer"
        assert latency > 0, "Error: latency should be greater than zero"

        self.__link_id = link_id
        self.__latency = latency
        self.__output_port = None
        self.__input_port = None
        self.__pipeline = deque(maxlen = latency)
        self.__credit_pipeline = deque(maxlen = latency)
        self.__cycle = -1

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

    def get_input_port(self):
        return self.__input_port

    def get_output_port(self):
        return self.__output_port

    def get_pipeline(self):
        return self.__pipeline

    def get_credit_pipeline(self):
        return self.__credit_pipeline

    def is_space(self, pipeline):
        if len(pipeline) < pipeline.maxlen:
            return True
        return False

    def push_pkt(self, item, current_cycle, pipeline_type):
        assert item is not None, "Error: item cannot be None"
        assert pipeline_type in ('data', 'credit'), "Error: pipeline_type must be 'data' or 'credit'"

        pipeline = self.get_pipeline() if pipeline_type == "data" else self.get_credit_pipeline()

        if self.is_space(pipeline):
            pipeline.append([item, current_cycle])
            return 0

        return -1


    def advance(self, current_cycle):
        """
        @brief      Advances the packets in the pipeline.
        @param      current_cycle - integer value representing the simulation time.
        """
        latency = self.get_latency()
        pipeline = self.get_pipeline()
        credit_pipeline = self.get_credit_pipeline()

        # Advance the packets
        if len(pipeline) > 0:
            pkt = pipeline[0]
            if pkt[1] + latency == current_cycle:
                pipeline.popleft()
                self.get_input_port().recv_from_link(pkt[0])

        # Advance the credits
        if len(credit_pipeline) > 0:
            credit_pkt = credit_pipeline[0]
            if credit_pkt[1] + latency == current_cycle:
                credit_pipeline.popleft()
                self.get_output_port().increment_credit()