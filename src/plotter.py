"""
@file       plotter.py
@brief      This class helps in plotting graphs.
@author     Akshay Joshi
"""

import matplotlib.pyplot as plt

class Plotter:
    """
    @class      Plotter
    """
    def __init__(self, log, node_id):
        """
        @brief      A constructor for the Plotter class
        @param      log  - list of {key, value} data used for the plot
        @param      node_id - identifier of the node 
        """
        self.__log = log
        self.__node_id = node_id
    
    def plot_graph(self, event):
        """
        @brief      Plots the graph based on the data in log
        """
        cycles = sorted(self.__log.keys())
        successes = [int(self.__log[cycle]) for cycle in cycles]

        plt.figure(figsize = (10, 4))
        plt.bar(cycles, successes, color = 'skyblue', edgecolor = 'black', width = 0.8)
        plt.title(f"{event} Success per Cycle - {self.__node_id}")
        plt.xlabel("Cycle")
        plt.ylabel(f"{event} (1=Yes, 0=No)")
        plt.ylim(0, 1.2)
        plt.xticks(cycles)
        plt.grid(axis = 'y', linestyle = '--', alpha = 0.7)

        filename = f"../outputs/{self.__node_id}_{event}_log.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()