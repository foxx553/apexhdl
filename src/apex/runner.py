import argparse
import json
import itertools
from dataclasses import fields
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, KeysView, Optional, get_args, get_origin, Literal, Union

from apex.context import Context
from apex.pipeline import Pipeline
from apex.generation_stage.generation_registry import GenerationRegistry
from apex.simulation_stage.simulation_registry import SimulationRegistry
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry
from apex.implementation_stage.implementation_registry import ImplementationRegistry
import apex.utils as utils

class Runner:
    """
    Class to parse args and init execution, eventually managing benchmarking mode
    """

    _parser: ArgumentParser
    """Parser used for dictionary building"""

    def __init__(self):
        """
        Execution initialization
        """

        # Loading all variants in registries
        GenerationRegistry.load_variants()
        SimulationRegistry.load_variants()
        SynthesisRegistry.load_variants()
        ImplementationRegistry.load_variants()

        # Init parser
        self._parser = argparse.ArgumentParser(description="ApexHDL: A Tool for Generating/Benchmarking Unary and Binary Function Evaluators on FPGA")

        # Config argument
        conf: Any = self._parser.add_argument_group("Config")
        conf.add_argument("--config", type=Path, help="Path to a JSON file containing configuration")

        # Context-related arguments, deduced from Context definition
        groups: dict[str, Any] = {}
        for field in fields(Context):

            # Extract metadata and create group
            group: str = field.metadata.get("group", "General")
            description: str = field.metadata.get("description", "")
            allow_multiple: bool = field.metadata.get("allow_multiple", False)
            if group not in groups:
                groups[group] = self._parser.add_argument_group(group)
            current_group: Any = groups[group]
            origin: Optional[Any] = get_origin(field.type)
            args: tuple[Any, ...] = get_args(field.type)

            # Start building field args
            kwargs: dict[str, Any] = {
                "help": description,
                "dest": field.name
            }

            # Extract actual type of Union/Optional field
            if origin is Union:
                actual_types: list[Any] = [a for a in args if a is not type(None)]
                actual_type: Any = actual_types[0]
                origin = get_origin(actual_type)
                args = get_args(actual_type)
            else:
                actual_type = field.type

            # Allow multiple values when metadata specify it
            if allow_multiple:
                kwargs["nargs"] = "+"

            # Allow a specific set of choices for Literal field
            if origin is Literal:
                kwargs["choices"] = args
                kwargs["type"] = type(args[0])
            else:
                kwargs["type"] = actual_type

            # Build and add the flag to the parser
            flag: str = f"--{field.name.replace('_', '-')}"
            current_group.add_argument(flag, **kwargs)
        

    def build_dict(self) -> dict[str, Any]:
        """
        Parsing args to create args dictionary, with CLI overwriting JSON default config

        Returns:
            dict[str, Any]: dictionary with all args and their value(s)
        """

        # If there's a JSON config file, defining default values
        initial_args: tuple[Namespace, list[str]] = self._parser.parse_known_args()
        config_path: Optional[Any] = getattr(initial_args[0], 'config', None)
        if config_path:
            json_file: Path = Path(config_path)
            if not json_file.exists():
                self._parser.error(f"JSON configuration file not found: {json_file}")
            with open(json_file, 'r') as f:
                config_data: dict[str, Any] = json.load(f)
                self._parser.set_defaults(**config_data)

        # Parsing CLI args
        args: Namespace = self._parser.parse_args()

        # Removing the "json" key before building the context
        args_dict: dict[str, Any] = vars(args).copy()
        args_dict.pop('config', None)
        
        return args_dict
    
    def run(self, args_dict: dict[str, Any]) -> bool:
        """
        Running the pipeline(s), eventually managing benchmarking mode

        Parameters:
            args_dict (dict[str, Any]): dictionary with all args and their value(s)
        
        Returns:
            bool: Whether the overall execution was successful or not
        """

        # Generating all possible configurations
        keys: KeysView[str] = args_dict.keys()
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
                current_args_dict: dict[str, Any] = dict(zip(keys, config))
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
    
