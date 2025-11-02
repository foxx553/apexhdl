from utils import parse_function, clamp_nearest
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os

def run_testbench(evaluator_name):
    """ Run testbench using GHDL """

    # Note = Delete GHDL work directory to trigger full analysis
    if os.path.exists("./work-obj08.cf"):
        os.remove("./work-obj08.cf")
    
    # Run GHDL simulation
    subprocess.run(["ghdl", "-a", "--std=08", f"../sources/{evaluator_name}/{evaluator_name}.vhd", f"../sources/{evaluator_name}/tb_{evaluator_name}.vhd"], check=True)
    subprocess.run(["ghdl", "-e", "--std=08", f"tb_{evaluator_name}"], check=True)
    subprocess.run(["ghdl", "-r", "--std=08", f"tb_{evaluator_name}"], check=True)

def plot_comparison(args):
    """ Plot evaluator results """

    # Args extraction
    evaluator_name = args[0]
    function_str = args[1]
    data_width = int(args[2])
    x_min, x_max, y_min, y_max = map(int, args[3:7])

    # Validation parameters
    results_file_path = f"../sources/{evaluator_name}/results_{evaluator_name}.txt"
    math_function = parse_function(function_str)
    x_step = (x_max - x_min) / (2 ** data_width)
    y_step = (y_max - y_min) / (2 ** data_width)

    # Read results file
    raw_y_values = []
    with open(results_file_path, 'r') as file:
        for line in file:
            # Strip whitespace and split by comma
            parts = line.strip().split(',')
            if len(parts) == 2:
                raw_y_values.append(int(parts[1]))

    # Computing theoretical and experimental values
    x_values = np.arange(x_min, x_max, 0.001)
    y_evaluator = []
    y_theoretical = []
    absolute_error = []
    for x_value in x_values:
        theoretical = math_function(x_value)
        evaluator = y_min + raw_y_values[clamp_nearest(x_value, x_min, x_step, data_width)] * y_step
        y_theoretical.append(theoretical)
        y_evaluator.append(evaluator)
        absolute_error.append(abs(theoretical - evaluator))

    # Computing and saving experimental plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_evaluator, color='red', linewidth=1)
    plt.title('Experimental values')
    plt.xlabel('x')
    plt.ylabel('Values')
    plt.grid(True)
    plt.savefig(f"../sources/{evaluator_name}/plot_experimental_{evaluator_name}.png")

    # Computing and saving theoretical plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_theoretical, color='blue', linewidth=1)
    plt.title('Theoretical values')
    plt.xlabel('x')
    plt.ylabel('Values')
    plt.grid(True)
    plt.savefig(f"../sources/{evaluator_name}/plot_theoretical_{evaluator_name}.png")

    # Computing and saving comparison plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_theoretical, color='blue', linewidth=1, label='Theoretical values')
    plt.plot(x_values, y_evaluator, color='red', linewidth=1, label='Experimental values')
    plt.title('Theoretical values vs. experimental values')
    plt.xlabel('x')
    plt.ylabel('Values')
    plt.grid(True)
    plt.legend()
    plt.savefig(f"../sources/{evaluator_name}/plot_comparison_{evaluator_name}.png")

    # Computing and saving absolute error plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, absolute_error, color='blue', linewidth=1)
    plt.title('Absolute error of evaluator values')
    plt.xlabel('x')
    plt.ylabel('Absolute error')
    plt.grid(True)
    plt.savefig(f"../sources/{evaluator_name}/plot_error_{evaluator_name}.png")

