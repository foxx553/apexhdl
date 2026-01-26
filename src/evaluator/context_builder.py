import argparse
from argparse import ArgumentParser, _ArgumentGroup, Namespace
from pathlib import Path

from evaluator.context import Context

class ContextBuilder:
    """
    Class for building Context based on args
    """

    def __init__(self):
        """
        Context builder initialization
        """

        # Init parser
        self.parser: ArgumentParser = argparse.ArgumentParser(description="FPGAEvaluator - A CLI Tool for Generating and Validating Unary and Binary Function Evaluators")

        # --- General ---
        gen: _ArgumentGroup = self.parser.add_argument_group("General")
        gen.add_argument("--method-name", choices=["rom", "bipartite", "symmetric", "hybrid", "unary"], required=True, help="Name of the circuit generation method")
        gen.add_argument("--circuit-name", required=True, help="Name of the circuit generated")
        gen.add_argument("--output-folder-path", required=True, type=Path, help="Folder where all generated files will be put")

        # --- Maths ---
        maths: _ArgumentGroup = self.parser.add_argument_group("Maths")
        maths.add_argument("--math-function", required=True, help="Mathematical function to be approximated by the generated circuit")
        maths.add_argument("--x-min", required=True, type=float, help="Minimum X value of the approximation region")
        maths.add_argument("--x-max", required=True, type=float, help="Maximum X value of the approximation region")
        maths.add_argument("--y-min", required=True, type=float, help="Minimum Y value of the approximation region")
        maths.add_argument("--y-max", required=True, type=float, help="Maximum Y value of the approximation region")

        # --- Generation ---
        build: _ArgumentGroup = self.parser.add_argument_group("Generation")
        build.add_argument("--data-width", required=True, type=int, help="Number of bits of the approximation")
        build.add_argument("--segment-idx-width", type=int, help="Number of bits for indexing segments (if applicable)")
        build.add_argument("--group-idx-width", type=int, help="Number of bits for indexing groups of segments (if applicable)")

        # --- Software ---
        sw: _ArgumentGroup = self.parser.add_argument_group("Software")
        sw.add_argument("--simulation-tool", choices=["ghdl"], help="Software used for circuit simulation")
        sw.add_argument("--analysis-tool", choices=["vivado"], help="Software used for circuit analysis")
        sw.add_argument("--analysis-mode", choices=["synth", "impl"], help="Whether the analysis is done post-synthesis or post-implementation")
        sw.add_argument("--implementation-tool", choices=["vivado"], help="Software used for circuit implementation and bitstream generation")

        # --- Hardware ---
        hw: _ArgumentGroup = self.parser.add_argument_group("Hardware")
        hw.add_argument("--fpga-board", help="Part number of the target FPGA")
        hw.add_argument("--ip-address", help="IP address for SSH connection to the target FPGA")
        hw.add_argument("--username", help="Username for SSH connection to the target FPGA")
        hw.add_argument("--password", help="Password for SSH connection to the target FPGA")
        hw.add_argument("--fpga-working-folder-path", help="Folder on the target FPGA in which all files will be sent and executed")

    def build(self) -> Context:
        """
        Parsing args to build Context object

        Returns:
            Context: Resulting context for pipeline execution
        """

        args: Namespace = self.parser.parse_args()
        return Context(**vars(args))