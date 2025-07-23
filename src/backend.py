"""
@file       backend.py
@brief      Provides the backend interface for building and executing custom simulations.
@author     Akshay Joshi
"""

import os
import argparse
import sys
import logging
logger = logging.getLogger(__name__)

from simulator import Simulator
from parser import Parser


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--nodes",
        type = str,
        required = True,
        help = "Relative path to the nodes csv file"
    )
    parser.add_argument(
        "--connections",
        type = str,
        required = True,
        help = "Relative path to the topology csv file"
    )
    parser.add_argument(
        "--inputs",
        type = str,
        required = True,
        help = "Relative path to the directory containing user-defined node implementations"
    )
    parser.add_argument(
        "--cycles",
        type = int,
        default = 10,
        help = "Number of simulation cycles (default: 10)"
    )
    parser.add_argument(
        "--log-level",
        type = str,
        default = "INFO",
        choices = ["DEBUG", "INFO", "WARNING", "ERROR", "OFF"],
        help = "Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-scope",
        type = str,
        default = "all",
        help = "comma-separated list of module names to include in logging (e.g., 'node,producer'). Use 'all' for everything"
    )

    return parser.parse_args()

def setup_logger(args):
    if args.log_level == "OFF":
        logging.disable(logging.CRITICAL)
    else:
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.basicConfig(
            filename = "../outputs/simulation.log",
            filemode = "w",
            level = getattr(logging, args.log_level),
            format = "[%(levelname)s] %(name)s: %(message)s",
        )

        class ModuleFilter(logging.Filter):
            def __init__(self, allowed_modules):
                super().__init__()
                self.allowed_modules = allowed_modules

            def filter(self, record):
                if "all" in self.allowed_modules:
                    return True
                return any(mod in record.name for mod in self.allowed_modules)

        allowed_modules = args.log_scope.split(",")
        filter = ModuleFilter(allowed_modules)
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(filter)

if __name__ == "__main__":
    args = parse_args()
    setup_logger(args)

    node_config = os.path.abspath(args.nodes)
    connection_config = os.path.abspath(args.connections)
    user_nodes_dir = os.path.abspath(args.inputs)

    if args.cycles <= 0:
        logger.error(f"Number of cycles must be positive. Got: {args.cycles}")
        sys.exit(-1)

    parser = Parser(node_config, connection_config, user_nodes_dir)

    sim = Simulator(args.cycles, parser)
    sim.setup()
    sim.run()
    sim.teardown()
