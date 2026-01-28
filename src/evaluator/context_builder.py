import argparse
import json
from argparse import ArgumentParser, _ArgumentGroup, Namespace
from pathlib import Path
from typing import Any, Dict

from evaluator.context import Context

class ContextBuilder:
    """
    Class for building Context based on args or a JSON configuration file.
    """

    parser: ArgumentParser
    """Parser used for Context building"""

    def __init__(self):
        """
        Context builder initialization
        """

        # Parser init
        self.parser = argparse.ArgumentParser(description="FPGAEvaluator - A CLI Tool for Generating and Validating Unary and Binary Function Evaluators")

        # Config
        conf: _ArgumentGroup = self.parser.add_argument_group("Config")
        conf.add_argument("--config", type=Path, help="Path to a JSON file containing configuration")

        # General
        gen: _ArgumentGroup = self.parser.add_argument_group("General")
        gen.add_argument("--method-name", choices=["rom", "bipartite", "symmetric", "hybrid", "unary"], help="Name of the circuit generation method")
        gen.add_argument("--circuit-name", help="Name of the circuit generated")
        gen.add_argument("--output-folder-path", type=Path, help="Folder where all generated files will be put")
        gen.add_argument("--step", choices=["sim", "rpt", "rpt-impl", "impl"], help="Steps done for the generation")

        # Maths
        maths: _ArgumentGroup = self.parser.add_argument_group("Maths")
        maths.add_argument("--math-function", help="Mathematical function to be approximated")
        maths.add_argument("--x-min", type=float, help="Minimum X value")
        maths.add_argument("--x-max", type=float, help="Maximum X value")
        maths.add_argument("--y-min", type=float, help="Minimum Y value")
        maths.add_argument("--y-max", type=float, help="Maximum Y value")

        # Generation
        build: _ArgumentGroup = self.parser.add_argument_group("Generation")
        build.add_argument("--data-width", type=int, help="Number of bits of the approximation")
        build.add_argument("--segment-idx-width", type=int, help="Number of bits for indexing segments")
        build.add_argument("--group-idx-width", type=int, help="Number of bits for indexing groups")

        # Software
        sw: _ArgumentGroup = self.parser.add_argument_group("Software")
        sw.add_argument("--simulation-tool", choices=["ghdl"], help="Software used for circuit simulation")
        sw.add_argument("--analysis-tool", choices=["vivado"], help="Software used for circuit analysis")
        sw.add_argument("--analysis-mode", choices=["synth", "impl"], help="Post-synthesis or post-implementation")
        sw.add_argument("--implementation-tool", choices=["vivado"], help="Software used for implementation")

        # Hardware
        hw: _ArgumentGroup = self.parser.add_argument_group("Hardware")
        hw.add_argument("--fpga-board", help="Part number of the target FPGA")
        hw.add_argument("--ip-address", help="IP address for SSH connection")
        hw.add_argument("--username", help="Username for SSH connection")
        hw.add_argument("--password", help="Password for SSH connection")
        hw.add_argument("--fpga-working-folder-path", help="Folder on the target FPGA")

    def build(self) -> Context:
        """
        Parsing args to build Context object, with CLI args overriding JSON configuration values

        Returns:
            Context: Resulting context for pipeline execution
        """

        # If there's a JSON config file, defining default values
        initial_args, _ = self.parser.parse_known_args()
        if initial_args.config:
            json_file: Path = Path(initial_args.config)
            if not json_file.exists():
                self.parser.error(f"JSON configuration file not found: {json_file}")
            with open(json_file, 'r') as f:
                config_data: Dict[str, Any] = json.load(f)
                self.parser.set_defaults(**config_data)

        # Parsing CLI args
        args: Namespace = self.parser.parse_args()

        # Removing the "json" key before building the context
        context_dict = vars(args).copy()
        context_dict.pop('config', None)

        return Context(**context_dict)