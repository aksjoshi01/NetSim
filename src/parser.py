"""
@file       parser.py
@brief      This class reads the input files and stores them in lists.
@author     Akshay Joshi
"""

import os
import csv
import sys

class NodeSetup:
    def __init__(self, module_name, class_name, node_id):
        self.module_name = module_name
        self.class_name = class_name
        self.node_id = node_id
    
    def get_module_name(self):
        return self.module_name

    def get_class_name(self):
        return self.class_name

    def get_node_id(self):
        return self.node_id

class ConnectionSetup:
    def __init__(self, src_node, op_id, dst_node, ip_id, credit, fifo_size, latency):
        self.src_node = src_node
        self.op_id = op_id
        self.dst_node = dst_node
        self.ip_id = ip_id
        self.credit = credit
        self.fifo_size = fifo_size
        self.latency = latency
        self.link_id = f"link_{src_node}_{op_id}_to_{dst_node}_{ip_id}"

    def get_src_node(self):
        return self.src_node

    def get_dst_node(self):
        return self.dst_node

    def get_op_id(self):
        return self.op_id

    def get_ip_id(self):
        return self.ip_id

    def get_credit(self):
        return self.credit
    
    def get_fifo_size(self):
        return self.fifo_size

    def get_latency(self):
        return self.latency

    def get_link_id(self):
        return self.link_id


class Parser:
    """
    @class      Parser
    """
    def __init__(self, node_config, connection_config, user_nodes_dir):
        """
        @brief      A constructor to the Parser class.
        @param      config_dir - path to the directory that contains the 
                    files to be parsed.
        """
        self.__node_config = node_config
        self.__connection_config = connection_config
        self.__user_nodes_dir = user_nodes_dir
        self.nodes = []
        self.connections = []

    def __read_file(self, filepath):
        """
        @brief      Reads the input file and returns its data.
        @param      filename - name of the input file to be parsed
        @return     a list of values read from the input file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File does not exist: {filepath}")
        with open(filepath, newline = '') as f:
            return list(csv.DictReader(f))

    def __parse_nodes(self):
        data = self.__read_file(self.__node_config)
        for row in data:
            module_name = row["module"]
            class_name = row["class"]
            node_id = row["node_id"]

            node = NodeSetup(module_name, class_name, node_id)
            self.nodes.append(node)

    def __parse_connections(self):
        data = self.__read_file(self.__connection_config)
        for row in data:
            src_node = row["src_node"]
            dst_node = row["dst_node"]
            op_id = row["src_port"]
            ip_id = row["dst_port"]
            
            try:
                credit = int(row["credit"])
                fifo_size = int(row["fifo_size"])
                latency = int(row["latency"])
            except ValueError:
                raise ValueError(f"Invalid integer")
            
            connection = ConnectionSetup(src_node, op_id, dst_node, ip_id, credit, fifo_size, latency)
            self.connections.append(connection)

    def parse(self):
        self.__parse_nodes()
        self.__parse_connections()
        if self.__user_nodes_dir not in os.sys.path:
            os.sys.path.append(self.__user_nodes_dir)