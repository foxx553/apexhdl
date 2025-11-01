from generation import evaluation_methods_map
from validation import run_testbench, plot_comparison
from utils import generate_testbench
import sys
import os

def main():

    # User manual
    if sys.argv[1] == "help":
        print(f"""
General usage: generate_evaluator.py <method> <evaluator_name> [args...]
Specific usage: Depending on <method>
    > rom: generate_evaluator.py rom <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > binary: generate_evaluator.py binary <evaluator_name> <function_of_x> <data_width> <offset_width> <x_min> <x_max> <y_min> <y_max>
    > unary: generate_evaluator.py unary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > hybrid: generate_evaluator.py hybrid <evaluator_name> <function_of_x> <data_width> <offset_width> <x_min> <x_max> <y_min> <y_max>
""")
        return

    # Args extraction and folder creation
    evaluator_type = sys.argv[1]
    evaluator_name = sys.argv[2]
    evaluation_method_args = sys.argv[2:]
    evaluation_method = evaluation_methods_map.get(evaluator_type)
    dir_path = f"../sources/{evaluator_name}"
    os.makedirs(dir_path, exist_ok=True)
    print(f"Note = Files will be generated in ../sources/{evaluator_type}")
    print("1/5 = Extracted generation arguments")

    # Evaluator generation
    if evaluation_method:
        vhdl_code = evaluation_method(evaluation_method_args)
        with open(f"../sources/{evaluator_name}/{evaluator_name}.vhd", "w") as file:
            file.write(vhdl_code)
    else:
        print(f"Error: Unknown method '{sys.argv[1]}'")
        return
    print("2/5 = Generated function evaluator")

    # Testbench generation
    tb_vhdl_code = generate_testbench(evaluator_name)
    with open(f"../sources/{evaluator_name}/tb_{evaluator_name}.vhd", "w") as file:
        file.write(tb_vhdl_code)
    print("3/5 = Generated testbench for function evaluator")

    # Testbench execution
    run_testbench(evaluator_name)
    print("4/5 = Run testbench")

    # Plot comparison results
    plot_comparison(evaluator_type, evaluation_method_args)
    print("5/5 = Plot comparison results")

if __name__ == "__main__":
    main()