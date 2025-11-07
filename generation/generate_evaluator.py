from helpers.generation import evaluation_methods_map
from helpers.validation import run_testbench, plot_comparison, generate_testbench
from helpers.analysis import generate_top, run_vivado_analysis
from helpers.implementation import run_vivado_implementation, generate_notebook
from helpers.utils import extract_hwh_from_xsa
import sys
import os
import nbformat as nbf

def main():

    # User manual
    if sys.argv[1] == "help":
        print(f"""
* Specs:
    > Generates a synthetizable VHDL module for function evaluation
    > Generates a testbench for VHDL module validation
    > Runs the testbench using GHDL & plots the comparison with theoretical results
    > Generates full report on timing/resources/power using Vivado, for PYNQ-Z2 board
    > Generates full design on Vivado, providing ready-to-use bitstream, hardware-handoff & notebook files for PYNQ-Z2 framework
    
* Notes:
    > 1) Simulation requires lightweight GHDL installation
    > 2) Reports & implementation require Vivado installation and board files for PYNQ-Z2 (xc7z020clg400-1)
    > 3) Real test requires PYNQ-Z2 board, and an SD card flashed with PYNQ-Z2 boot image
    > Stopping after steps 1), 2) or 3) can be done by using respectively --sim, --rpt, --bit (default value)
    > For documentation & resources about PYNQ-Z2, see https://www.tulembedded.com/FPGA/ProductsPYNQ-Z2.html
              
* General usage: 
    > generate_evaluator.py <method> <evaluator_name> [args...]
              
* Specific usage: Depending on <method>
    > rom: generate_evaluator.py rom <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > binary: generate_evaluator.py binary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max> <segment_idx_width> <group_idx_width>
    > unary: generate_evaluator.py unary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>
    > hybrid: generate_evaluator.py hybrid <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max> <segment_idx_width>
""")
        return

    # Args extraction and folder creation
    print("Extracting evaluator parameters & creating directories...")
    evaluator_type = sys.argv[1]
    evaluator_name = sys.argv[2]
    data_width = sys.argv[4]
    evaluation_method_args = sys.argv[2:]
    last_arg = sys.argv[len(sys.argv) - 1]
    step_map, step_count = ["--sim", "--rpt", "--bit"], [5, 7, 8]
    step_specifier = 2 if last_arg not in step_map else step_map.index(last_arg)
    number_of_steps = step_count[step_specifier]
    evaluation_method = evaluation_methods_map.get(evaluator_type)
    base_path = f"../output/{evaluator_name}"
    subdirs = ["vhdl", "sim"]
    if step_specifier > 0:
        subdirs.append("rpt")
        if step_specifier > 1:
            subdirs.append("bit")
    for subdir in subdirs:
        dir_path = os.path.join(base_path, subdir)
        os.makedirs(dir_path, exist_ok=True)
    print(f"[1/{number_of_steps}] Extracted evaluator parameters & creates directories")
    print(f"[Note] Files will be generated in folder ../output/{evaluator_name}")

    # Evaluator generation
    print("Generating function evaluator...")
    vhdl_code = evaluation_method(evaluation_method_args)
    with open(f"../output/{evaluator_name}/vhdl/{evaluator_name}.vhd", "w") as file:
        file.write(vhdl_code)
    print(f"[2/{number_of_steps}] Generated function evaluator")

    # Testbench generation
    print("Generating testbench for function evaluator...")
    tb_vhdl_code = generate_testbench(evaluator_type, evaluation_method_args)
    with open(f"../output/{evaluator_name}/vhdl/tb_{evaluator_name}.vhd", "w") as file:
        file.write(tb_vhdl_code)
    print(f"[3/{number_of_steps}] Generated testbench for function evaluator")

    # Testbench execution
    print("Running testbench using GHDL...")
    run_testbench(evaluator_name)
    print(f"[4/{number_of_steps}] Finished running testbench using GHDL")

    # Plot comparison results
    print("Plotting comparison results...")
    plot_comparison(evaluation_method_args)
    print(f"[5/{number_of_steps}] Finished plotting comparison results")

    # --sim barrier
    if step_specifier == 0:
        print(f"[Completed] Successfully generated sim files in folder ../output/{evaluator_name}")
        return

    # Top-module generation
    print("Generating top module for function evaluator...")
    tb_vhdl_code = generate_top(evaluator_type, evaluation_method_args)
    with open(f"../output/{evaluator_name}/vhdl/top_{evaluator_name}.vhd", "w") as file:
        file.write(tb_vhdl_code)
    print(f"[6/{number_of_steps}] Generated top module for function evaluator")

    # Vivado reporting of function evaluator
    print("Running evaluator analysis with Vivado...")
    run_vivado_analysis(evaluator_name)
    print(f"[7/{number_of_steps}] Finished running Vivado analysis")

    # --rpt barrier
    if step_specifier == 1:
        print(f"[Completed] Successfully generated sim & rpt files in folder ../output/{evaluator_name}")
        return

    # Vivado wrapping é implementation of function evaluator
    print("Running evaluator wrapping & implementation with Vivado...")
    evaluator_notebook = generate_notebook(evaluation_method_args)
    with open(f"../output/{evaluator_name}/bit/{evaluator_name}.ipynb", "w") as file:
        nbf.write(evaluator_notebook, file)
    run_vivado_implementation(evaluator_name, data_width)
    extract_hwh_from_xsa(f"../output/{evaluator_name}/bit/{evaluator_name}.xsa", f"{evaluator_name}.hwh")
    print(f"[8/{number_of_steps}] Finished running Vivado wrapping & implementation")

    print(f"[Completed] Successfully generated all files in folder ../output/{evaluator_name}")

if __name__ == "__main__":
    main()