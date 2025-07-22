"""
@file       parser.py
@brief      This class reads the input files and stores them in lists.
@author     Akshay Joshi
"""

import os
import csv

class Parser:
    """
    @class      Parser
    """
    def __init__(self, config_dir):
        """
        @brief      A constructor to the Parser class.
        @param      config_dir - path to the directory that contains the 
                    files to be parsed.
        """
        self.__config_dir = config_dir
        self.__node_specs = []
        self.__connection_specs = []

    def get_connection_specs(self):
        return self.__connection_specs

    def get_node_specs(self):
        return self.__node_specs

    def parse(self):
        """
        @brief      A wrapper that calls the actual parser method by passing
                    filename as an argument to it.
        """
        self.__node_specs = self.__parse_csv("nodes.csv")
        self.__connection_specs = self.__parse_csv("connections.csv")

    def __parse_csv(self, filename):
        """
        @brief      Reads the input file and returns its data.
        @param      filename - name of the input file to be parsed
        @return     a list of values read from the input file
        """
        filepath = os.path.join(self.__config_dir, filename)
        with open(filepath, newline = '') as f:
            return list(csv.DictReader(f))