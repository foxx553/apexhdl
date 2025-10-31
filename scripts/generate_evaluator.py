from evaluation_methods import evaluation_methods_map
import sys

def main():

    if sys.argv[1] == "help":
        print(f"""
General usage: generate_evaluator.py <method> <evaluator_name> [args...]
Specific usage: Depending on <method>
    > lut: generate_evaluator.py lut <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > binary: generate_evaluator.py binary <evaluator_name> <function_of_x> <data_width> <offset_width> <x_min> <x_max> <y_min> <y_max>
    > unary: generate_evaluator.py unary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > hybrid: generate_evaluator.py hybrid <evaluator_name> <function_of_x> <data_width> <offset_width> <x_min> <x_max> <y_min> <y_max>
""")
        return

    evaluator_name = sys.argv[2]
    evaluation_method_args = sys.argv[2:]
    evaluation_method = evaluation_methods_map.get(sys.argv[1])

    if evaluation_method:
        vhdl_code = evaluation_method(evaluation_method_args)
        with open(f"../sources/{evaluator_name}.vhd", "w") as file:
            file.write(vhdl_code)
        print(f"Successfully generated the evaluator {evaluator_name}.vhd in the sources folder")
    else:
        print(f"Error: Unknown method '{sys.argv[1]}'")

if __name__ == "__main__":
    main()