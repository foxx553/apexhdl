import argparse
from argparse import ArgumentParser, _ArgumentGroup, Namespace
from pathlib import Path

from evaluator.context import Context
from evaluator.pipeline import Pipeline
from args_parser import ArgsParser

# Main function
def main():
    """
    Main function, entry point of the FPGAEvaluator code
    """

    # Parsing and mapping to Context dataclass
    parser: ArgsParser = ArgsParser()
    ctx: Context = parser.parse()

    # Building the corresponding pipeline
    pipeline: Pipeline = Pipeline(ctx)

    # Running the pipeline
    pipeline.run()

# Entry point
if __name__ == "__main__":
    main()