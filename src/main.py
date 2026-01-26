from evaluator.context import Context
from evaluator.pipeline import Pipeline
from evaluator.context_builder import ContextBuilder

# Main function
def main():
    """
    Main function, entry point of the FPGAEvaluator code
    """

    # Parsing and mapping to Context dataclass
    builder: ContextBuilder = ContextBuilder()
    ctx: Context = builder.build()

    # Building the corresponding pipeline
    pipeline: Pipeline = Pipeline(ctx)

    # Running the pipeline
    pipeline.run()

# Entry point
if __name__ == "__main__":
    main()