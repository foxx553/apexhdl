from typing import Any, Dict

from evaluator.context import Context
from evaluator.pipeline import Pipeline
from evaluator.initializer import Initializer

# Main function
def main():
    """
    Main function, entry point of the FPGAEvaluator code
    """

    # Parsing args
    initializer: Initializer = Initializer()
    args_dict: Dict[str, Any] = initializer.build_dict()

    # Running pipeline(s)
    initializer.run(args_dict)

# Entry point
if __name__ == "__main__":
    main()