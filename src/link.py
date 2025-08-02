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
    def __init__(self, link_id, latency, vc_ids):
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
        self.__pipeline: deque = deque(maxlen=latency)
        self.__credit_pipeline: deque = deque(maxlen=latency)

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

    def __is_space(self, pipeline):
        return len(pipeline) < pipeline.maxlen
    
    def push_pkt(self, pkt, current_cycle):
        assert pkt is not None, "Error: pkt cannot be None"

        pipeline = self.__pipeline if isinstance(pkt, Packet) else self.__credit_pipeline
        if self.__is_space(pipeline):
            pipeline.append([pkt, current_cycle])
            return 0

        return -1

    def __advance_pipeline(self, pipeline, current_cycle):
        if len(pipeline) > 0:
            pkt = pipeline[0]
            if pkt[1] + self.__latency == current_cycle:
                pipeline.popleft()
                if isinstance(pkt[0], Packet):
                    logger.debug("Link has delivered data packet")
                    self.__input_port.push_pkt(pkt[0])
                else:
                    logger.debug("Link has delivered credit packet")
                    self.__output_port.push_pkt(pkt[0], current_cycle)

    def advance(self, current_cycle):
        """
        @brief      Advances the packets in the pipeline.
        @param      current_cycle - integer value representing the simulation time.
        """
        self.__advance_pipeline(self.__pipeline, current_cycle)
        self.__advance_pipeline(self.__credit_pipeline, current_cycle)