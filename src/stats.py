"""
@file       stats.py
@brief      Collects various statistics and prints the summary.
@author     Akshay Joshi
"""

from collections import defaultdict

class Stats:
    def __init__(self):
        self.total_cycles = 0
        self.total_pkts_sent = 0
        self.total_pkts_dlvrd = 0
        self.per_cycle_link_utilization = []
        self.node_activity = defaultdict(dict)
        self.node_stats = defaultdict(lambda: {
            "pkts_sent": 0,
            "pkts_recvd": 0
        })
        self.link_stats = defaultdict(lambda: {
            "utilized_cycles": 0,
            "total_pkts_transmitted": 0
        })

    def increment_pkt_sent(self, node_id):
        self.total_pkts_sent += 1
        self.node_stats[node_id]["pkts_sent"] += 1

    def increment_pkt_recvd(self, node_id):
        self.total_pkts_dlvrd += 1
        self.node_stats[node_id]["pkts_recvd"] += 1

    def link_transmit(self, link_id, active):
        stats = self.link_stats[link_id]
        if active:
            stats["utilized_cycles"] += 1
            stats["total_pkts_transmitted"] += 1

    def log_node_activity(self, node_id, cycle, active):
        self.node_activity[node_id][cycle] = active

    def start_cycle(self):
        self.total_cycles += 1
        self.per_cycle_link_utilization.append(set())

    def record_link_active(self, link_id):
        self.per_cycle_link_utilization[-1].add(link_id)

    def dump_summary(self):
        print(f"\n===== Simulation Summary =====")
        print(f"Total cycles: {self.total_cycles}")
        print(f"Total packets sent: {self.total_pkts_sent}")
        print(f"Total packets received: {self.total_pkts_dlvrd}")
        print(f"\n--- Per Node ---")
        for node, stats in self.node_stats.items():
            print(f"Node {node}: Sent = {stats['pkts_sent']}, Received = {stats['pkts_recvd']}")

        print(f"\n--- Per Link ---")
        for link, stats in self.link_stats.items():
            utilization = stats["utilized_cycles"] / self.total_cycles if self.total_cycles else 0
            print(f"Link {link}: Utilization = {utilization:.2%}, Packets Transmitted = {stats['total_pkts_transmitted']}")

        self.generate_plots()


    def generate_plots(self):
        from plotter import Plotter
        for node_id, activity in self.node_activity.items():
            plotter = Plotter(activity, node_id)
            plotter.plot_graph("Activity")