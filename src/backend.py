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

from node import Node
from link import Link
from packet import Packet
from port import OutputPort, InputPort
from simulator import Simulator
from parser import Parser
from plotter import Plotter

def validate_directory(path, name):
    if not os.path.exists(path):
        logger.error(f"{name} directory does not exist: {path}")
        sys.exit(-1)
    if not os.path.isdir(path):
        logger.error(f"{name} path is not a directory: {path}")
        sys.exit(-1)


def parse_args():
    parser = argparse.ArgumentParser(description="Run network simulation.")

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the directory containing topology CSV files"
    )

    parser.add_argument(
        "--inputs",
        type=str,
        required=True,
        help="Path to the directory containing user-defined node implementations"
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=10,
        help="Number of simulation cycles (default: 10)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "OFF"],
        help="Set the logging level (default: INFO)"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.log_level == "OFF":
        logging.disable(logging.CRITICAL)
    else:
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.basicConfig(
            level=getattr(logging, args.log_level),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )

    config_dir = os.path.abspath(args.config)
    user_nodes_dir = os.path.abspath(args.inputs)

    # Validate directories
    validate_directory(config_dir, "Config")
    validate_directory(user_nodes_dir, "Inputs")

    # Validate number of cycles
    if args.cycles <= 0:
        logger.error(f"Number of cycles must be positive. Got: {args.cycles}")
        sys.exit(-1)

    # Log simulation setup
    logger.info(f"Config directory: {config_dir}")
    logger.info(f"Inputs directory: {user_nodes_dir}")
    logger.info(f"Number of cycles: {args.cycles}")

    # Run simulation
    parser = Parser(config_dir)
    parser.parse()

    sim = Simulator(args.cycles)
    sim.build_nodes(parser, user_nodes_dir)
    sim.build_connections(parser)
    sim.run()
    sim.get_stats()
