import argparse
import json
import itertools
from dataclasses import fields
from argparse import ArgumentParser, _ArgumentGroup, Namespace
from pathlib import Path
from typing import Any, Dict, get_args, get_origin, Literal, Union

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
        self.parser = argparse.ArgumentParser(description="ApexHDL: A Tool for Generating/Benchmarking Unary and Binary Function Evaluators on FPGA")

        # "Meta" arguments
        conf: _ArgumentGroup = self.parser.add_argument_group("Config")
        conf.add_argument("--config", type=Path, help="Path to a JSON file containing configuration")

        # Context-related arguments, deduced from Context definition
        groups = {}
        for field in fields(Context):

            # Extract metadata and create group
            group_name = field.metadata.get("group", "General")
            help_text = field.metadata.get("help", "")
            if group_name not in groups:
                groups[group_name] = self.parser.add_argument_group(group_name)
            current_group = groups[group_name]
            kwargs = {
                "help": help_text,
                "dest": field.name
            }
            origin = get_origin(field.type)
            args = get_args(field.type)

            # Extract actual type of Union/Optional field
            if origin is Union:
                actual_types = [a for a in args if a is not type(None)]
                inner_type = actual_types[0]
                origin = get_origin(inner_type)
                args = get_args(inner_type)
            else:
                inner_type = field.type

            # Allow multiple values for list field
            if origin is list or inner_type is list:
                kwargs["nargs"] = "+"
                if args:
                    inner_type = args[0]
                    origin = get_origin(inner_type)
                    args = get_args(inner_type)

            # Allow a specific set of choices for Literal field
            if origin is Literal:
                kwargs["choices"] = args
                kwargs["type"] = type(args[0])
            else:
                kwargs["type"] = inner_type

            # Build and add the flag to the parser
            flag = f"--{field.name.replace('_', '-')}"
            current_group.add_argument(flag, **kwargs)
        

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
    
