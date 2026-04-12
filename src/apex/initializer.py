import argparse
import json
from argparse import ArgumentParser, _ArgumentGroup, Namespace
from pathlib import Path
from typing import Any, Dict
import itertools

from apex.context import Context
from apex.pipeline import Pipeline
from apex.generation_stage.generation_registry import GenerationRegistry
from apex.simulation_stage.simulation_registry import SimulationRegistry
from apex.analysis_stage.analysis_registry import AnalysisRegistry
from apex.implementation_stage.implementation_registry import ImplementationRegistry
import apex.utils as utils

class Initializer:
    """
    Class to parse args and init execution, eventually managing benchmarking mode
    """

    parser: ArgumentParser
    """Parser used for dictionary building"""

    def __init__(self):
        """
        Execution initialization
        """

        # Loading all variants in registries
        GenerationRegistry.load_variants()
        SimulationRegistry.load_variants()
        AnalysisRegistry.load_variants()
        ImplementationRegistry.load_variants()

        # Init parser
        self.parser = argparse.ArgumentParser(description="ApexHDL - A CLI Tool for Generating and Validating Unary and Binary Function Evaluators")

        # Config
        conf: _ArgumentGroup = self.parser.add_argument_group("Config")
        conf.add_argument("--config", type=Path, help="Path to a JSON file containing configuration")

        # General
        gen: _ArgumentGroup = self.parser.add_argument_group("General")
        gen.add_argument("--method-name", nargs="+", choices=["rom", "bipartite", "symmetric", "hybrid", "unary"], help="Name of the circuit generation method")
        gen.add_argument("--circuit-name", help="Name of the circuit generated")
        gen.add_argument("--output-folder-path", type=Path, help="Folder where all generated files will be put")
        gen.add_argument("--step", choices=["sim", "rpt", "rpt-impl", "impl"], help="Steps done for the generation (sim = simulation-only, rpt = analysis after synthesis, rpt-impl = analysis after place/route, impl = implementation)")

        # Maths
        maths: _ArgumentGroup = self.parser.add_argument_group("Maths")
        maths.add_argument("--math-function", nargs="+", help="Mathematical function to be approximated")
        maths.add_argument("--x-min", type=float, help="Minimum X value")
        maths.add_argument("--x-max", type=float, help="Maximum X value")
        maths.add_argument("--y-min", type=float, help="Minimum Y value")
        maths.add_argument("--y-max", type=float, help="Maximum Y value")

        # Generation
        build: _ArgumentGroup = self.parser.add_argument_group("Generation")
        build.add_argument("--data-width", nargs="+", type=int, help="Number of bits of the approximation")
        build.add_argument("--segment-idx-width", type=int, help="Number of bits for indexing segments")
        build.add_argument("--group-idx-width", type=int, help="Number of bits for indexing groups")

        # Software
        sw: _ArgumentGroup = self.parser.add_argument_group("Software")
        sw.add_argument("--simulation-tool", choices=["ghdl"], help="Software used for circuit simulation")
        sw.add_argument("--analysis-tool", choices=["vivado"], help="Software used for circuit analysis")
        sw.add_argument("--implementation-tool", choices=["vivado"], help="Software used for implementation")

        # Hardware
        hw: _ArgumentGroup = self.parser.add_argument_group("Hardware")
        hw.add_argument("--fpga-board", help="Part number of the target FPGA")
        hw.add_argument("--ip-address", help="IP address for SSH connection")
        hw.add_argument("--username", help="Username for SSH connection")
        hw.add_argument("--password", help="Password for SSH connection")
        hw.add_argument("--fpga-working-folder-path", help="Folder on the target FPGA")

    def build_dict(self) -> dict:
        """
        Parsing args to create args dictionary, with CLI overwriting JSON default config

        Returns:
            dict: Dictionary with all args and their value(s)
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
        args_dict: Dict[str, Any] = vars(args).copy()
        args_dict.pop('config', None)
        
        return args_dict
    
    def run(self, args_dict: Dict[str, Any]) -> bool:
        """
        Running the pipeline(s), eventually managing benchmarking mode

        Parameters:
            args_dict (Dict[str, Any]): Dictionary with all args and their value(s)
        
        Returns:
            bool: Whether the overall execution was successful or not
        """

        # Generating all possible configurations
        keys: list[str] = args_dict.keys()
        values: list[list[Any]] = [value if isinstance(value, list) else [value] for value in args_dict.values()]
        configurations: list[Any] = list(itertools.product(*values))

        # Normal mode
        if len(configurations) == 1:

            # Just running the only configuration
            ctx: Context = Context(**args_dict)
            pipeline: Pipeline = Pipeline(ctx)
            pipeline.run()

        # Benchmarking mode
        elif len(configurations) > 1:

            # Initializing necessary variables/files
            counter: int = 1
            benchmark_name: str = args_dict["circuit_name"]
            output_folder: Path = args_dict["output_folder_path"]
            utils.create_benchmark_csv(output_folder, benchmark_name)

            # Running all possible configurations
            for config in configurations:

                # Building the current configuration
                current_args_dict: Dict[str, Any] = dict(zip(keys, config))
                current_ctx: Context = Context(**current_args_dict)

                # Adding ID to circuit_name for uniqueness
                current_ctx.circuit_name = current_ctx.circuit_name + f"{counter:03}"
                counter = counter + 1

                # Running the current configuration
                current_pipeline: Pipeline = Pipeline(current_ctx)
                current_pipeline.run()

                # Appending the results in the CSV
                utils.append_benchmark_csv(output_folder, benchmark_name, current_ctx)

        return True
    
