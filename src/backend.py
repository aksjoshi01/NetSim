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

class Backend:
    def __init__(self):
        self.args = self.parse_args()
        self.setup_logger()
        if self.args.cycles <= 0:
            logger.error(f"Number of cycles must be positive. Got: {args.cycles}")
            sys.exit(-1)

    def parse_args(self):
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

    def add_logging_filter(self):
        class ModuleFilter(logging.Filter):
            def __init__(self, allowed_modules):
                super().__init__()
                self.allowed_modules = allowed_modules

            def filter(self, record):
                if "all" in self.allowed_modules:
                    return True
                return any(mod in record.name for mod in self.allowed_modules)

        allowed_modules = self.args.log_scope.split(",")
        filter = ModuleFilter(allowed_modules)
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(filter)

    def setup_logger(self):
        if self.args.log_level == "OFF":
            logging.disable(logging.CRITICAL)
        else:
            logging.getLogger('matplotlib').setLevel(logging.WARNING)
            logging.basicConfig(
                filename = "../outputs/simulation.log",
                filemode = "w",
                level = getattr(logging, self.args.log_level),
                format = "[%(levelname)s] %(name)s: %(message)s",
            )
            self.add_logging_filter()


if __name__ == "__main__":
    backend = Backend()

    node_config = os.path.abspath(backend.args.nodes)
    connection_config = os.path.abspath(backend.args.connections)
    user_nodes_dir = os.path.abspath(backend.args.inputs)

    parser = Parser(node_config, connection_config, user_nodes_dir)

    sim = Simulator(backend.args.cycles, parser)
    sim.setup()
    sim.run()
    sim.teardown()
