"""
@file       stats.py
@brief      Collects various statistics and prints the summary.
@author     Akshay Joshi
"""

from collections import defaultdict
from plotter import Plotter
import logging
logger = logging.getLogger(__name__)

class Stats:
    def __init__(self):
        self.__int_counters = defaultdict(int)
        self.__cycle_map = defaultdict(lambda: defaultdict(bool))

    # register a counter stat with unique name
    def register_counter(self, name):
        assert name not in self.__int_counters, "Error: duplicate names for stat counters"
        self.__int_counters[name]

    # increment the `name` counter - throw an error if no such name exists
    def incr_counter(self, name):
        assert name in self.__int_counters, "Error: counter name is invalid"
        self.__int_counters[name] += 1

    # get the value of the `name` counter - throw an error if name does not exist
    def get_counter(self, name):
        assert name in self.__int_counters, "Error: counter name is invalid"
        return self.__int_counters[name]

    def register_cycle_map(self, name):
        assert name not in self.__cycle_map, "Error: duplicate names for stat cycle map"
        self.__cycle_map[name]

    def record_cycle(self, name, cycle, val):
        assert name in self.__cycle_map, "Error: cycle_map name is invalid"
        self.__cycle_map[name][cycle] = val

    def get_cycle_map(self, name):
        assert name in self.__cycle_map, "Error: cycle_map name in invalid"
        return self.__cycle_map[name]

    def dump_summary(self):
        for name, val in self.__int_counters.items():
            logger.info(f"{name}: {val}")

        self.generate_plots()

    def generate_plots(self):
        for stat_name, cycle_count in self.__cycle_map.items():
            plotter = Plotter(cycle_count, stat_name)
            plotter.plot_graph()