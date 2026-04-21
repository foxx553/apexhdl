from typing import Any

from apex.runner import Runner

# Main function
def main():
    """
    Main function, entry point of the ApexHDL code
    """

    # Parsing args
    runner: Runner = Runner()
    args_dict: dict[str, Any] = runner.build_dict()

    # Running pipeline(s)
    runner.run(args_dict)

# Entry point
if __name__ == "__main__":
    main()