"""
@file       stats.py
@brief      Collects various statistics and prints the summary.
@author     Akshay Joshi
"""

from collections import defaultdict
from plotter import Plotter

class Stats:
    def __init__(self):
        self.int_counters = defaultdict(int)
        self.cycle_map = defaultdict(lambda: defaultdict(bool))

    def get_counter(self, name):
        return self.int_counters[name]

    def incr_counter(self, name):
        self.int_counters[name] += 1

    def get_cycle_map(self, name):
        return self.cycle_map[name]

    def record_cycle(self, name, cycle, val):
        self.cycle_map[name][cycle] = val

    def dump_summary(self):
        with open("../outputs/stats.log", "w") as file:
            for name, val in sorted(self.int_counters.items()):
                file.write(f"{name}: {val}\n")

        self.generate_plots()

    def generate_plots(self):
        for stat_name, cycle_count in self.cycle_map.items():
            plotter = Plotter(cycle_count, stat_name)
            plotter.plot_graph()