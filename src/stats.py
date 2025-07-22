"""
@file       stats.py
@brief      Collects various statistics and prints the summary.
@author     Akshay Joshi
"""

from collections import defaultdict
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)

class Stats:
    def __init__(self):
        self.__int_counters = defaultdict(int)
        self.__cycle_map = defaultdict(lambda: defaultdict(bool))
        self.__interval_counters = {}

    def register_interval_counter(self, name, interval):
        self.__interval_counters[name] = {
            "interval": interval,
            "buckets": defaultdict(int)
        }

    def incr_interval_counter(self, name, cycle):
        interval = self.__interval_counters[name]["interval"]
        bucket = (cycle // interval) * interval
        self.__interval_counters[name]["buckets"][bucket] += 1

    # register a counter stat with unique name
    def register_counter(self, name):
        assert name not in self.__int_counters, "Error: duplicate names for stat counters"
        self.__int_counters[name]

    # increment the `name` counter - throw an error if no such name exists
    def incr_counter(self, name, amount):
        assert name in self.__int_counters, "Error: counter name is invalid"
        self.__int_counters[name] += amount

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

    def plot_graph(self, cycle_map, name):
        cycles = sorted(cycle_map.keys())
        successes = [int(cycle_map[cycle]) for cycle in cycles]

        plt.figure(figsize = (10, 4))
        plt.bar(cycles, successes, color = 'skyblue', edgecolor = 'black', width = 0.8)
        plt.title(f"Activity per Cycle - {name}")
        plt.xlabel("Cycle")
        plt.ylabel(f"(1=Yes, 0=No)")
        plt.ylim(0, 1.2)
        plt.xticks(cycles)
        plt.grid(axis = 'y', linestyle = '--', alpha = 0.7)

        filename = f"../outputs/{name}_log.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()

    def plot_interval_graph(self, data, label, interval):
        x = sorted(data.keys())
        y = [data[i] for i in x]

        plt.figure(figsize=(10, 4))
        plt.plot(x, y, marker = 'o')
        plt.xlabel(f"Cycle interval (every {interval} cycles)")
        plt.ylabel("Packets sent")
        plt.title(f"{label}")
        plt.grid(True)
        filename = f"../outputs/{label}.png"
        plt.savefig(filename)
        plt.close()

    def dump_summary(self):
        for name, val in self.__int_counters.items():
            logger.info(f"{name}: {val}")

        self.generate_plots()

    def generate_plots(self):
        for stat_name, cycle_count in self.__cycle_map.items():
            self.plot_graph(cycle_count, stat_name)

        for name, info in self.__interval_counters.items():
            self.plot_interval_graph(info["buckets"], f"{name}", info["interval"])

