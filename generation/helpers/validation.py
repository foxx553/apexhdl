from .utils import parse_function, clamp_nearest
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
    subprocess.run(["ghdl", "-a", "--std=08", f"../output/{evaluator_name}/vhdl/{evaluator_name}.vhd", f"../output/{evaluator_name}/vhdl/tb_{evaluator_name}.vhd"], capture_output=True, check=True)
    subprocess.run(["ghdl", "-e", "--std=08", f"tb_{evaluator_name}"], capture_output=True, check=True)
    subprocess.run(["ghdl", "-r", "--std=08", f"tb_{evaluator_name}"], capture_output=True, check=True)

def plot_comparison(args):
    """ Plot evaluator results """

    # Args extraction
    evaluator_name = args[0]
    function_str = args[1]
    data_width = int(args[2])
    x_min, x_max, y_min, y_max = map(float, args[3:7])

    # Validation parameters
    results_file_path = f"../output/{evaluator_name}/sim/results_{evaluator_name}.txt"
    math_function = parse_function(function_str)
    x_step = (x_max - x_min) / (2 ** data_width)
    y_step = (y_max - y_min) / (2 ** data_width)
    theoretical_step = 0.001

    # Read results file
    raw_y_values = []
    with open(results_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                raw_y_values.append(int(parts[1]))

    # Computing theoretical and experimental values
    x_values = np.arange(x_min, x_max, theoretical_step)
    y_evaluator = []
    y_theoretical = []
    absolute_errors = []
    for x_value in x_values:
        theoretical = math_function(x_value)
        evaluator = y_min + raw_y_values[clamp_nearest(x_value, x_min, x_step, data_width)] * y_step
        y_theoretical.append(theoretical)
        y_evaluator.append(evaluator)
        absolute_errors.append(abs(theoretical - evaluator))
    mean_error = np.mean(absolute_errors)
    max_error = np.max(absolute_errors)
    with open(results_file_path, "a") as file:
        file.write(f"\n{"{:.3g}".format(max_error)},{"{:.3g}".format(mean_error)}")

    # Computing and saving experimental plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_evaluator, color='red', linewidth=3)
    plt.title('Experimental values', fontsize=30)
    plt.xlabel('x', fontsize=28)
    plt.ylabel('Values', fontsize=28)
    plt.grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig(f"../output/{evaluator_name}/sim/plot_experimental_{evaluator_name}.png")

    # Computing and saving theoretical plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_theoretical, color='blue', linewidth=3)
    plt.title('Theoretical values', fontsize=30)
    plt.xlabel('x', fontsize=28)
    plt.ylabel('Values', fontsize=28)
    plt.grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig(f"../output/{evaluator_name}/sim/plot_theoretical_{evaluator_name}.png")

    # Computing and saving comparison plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, y_theoretical, color='blue', linewidth=3, label='Theoretical values')
    plt.plot(x_values, y_evaluator, color='red', linewidth=3, label='Experimental values')
    plt.title('Theoretical values vs. experimental values', fontsize=30)
    plt.xlabel('x', fontsize=28)
    plt.ylabel('Values', fontsize=28)
    plt.grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
    plt.savefig(f"../output/{evaluator_name}/sim/plot_comparison_{evaluator_name}.png")

    # Computing and saving absolute error plot
    plt.figure(figsize=(20, 10))
    plt.plot(x_values, absolute_errors, color='blue', linewidth=3, label="Absolute errors")
    plt.plot(x_values, [max_error for _ in range(len(x_values))], color='red', linewidth=4, label=f"Max error = {"{:.3g}".format(max_error)}")
    plt.plot(x_values, [mean_error for _ in range(len(x_values))], color='orange', linewidth=4, label=f"Mean error = {"{:.3g}".format(mean_error)}")
    plt.title('Absolute error of evaluator values', fontsize=30)
    plt.xlabel('x', fontsize=28)
    plt.ylabel('Absolute error', fontsize=28)
    plt.grid(True)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
    plt.savefig(f"../output/{evaluator_name}/sim/plot_error_{evaluator_name}.png")

def generate_testbench(evaluator_type, args):
    """ Generates an exhaustive testbench for validation """

    # Args extraction
    evaluator_name = args[0]
    data_width = int(args[2])
    segment_idx_width, group_idx_width = 0, 0
    if evaluator_type == "binary" or evaluator_type == "hybrid":
        segment_idx_width = int(args[7])
        if evaluator_type == "binary":
            group_idx_width = int(args[8]) 

    return f"""
-------------------------------------
-- Engineers: Florian Delhon, Kevin Peymani
-- Target: PYNQ-Z2
-- Module Name: tb_{evaluator_name}
-- Description: Testbench for module {evaluator_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_{evaluator_name} is
end tb_{evaluator_name};

architecture arch_tb_{evaluator_name} of tb_{evaluator_name} is

    signal input_a : STD_LOGIC_VECTOR({data_width - 1} downto 0);
    signal result  : STD_LOGIC_VECTOR({data_width - 1} downto 0);

    file output_file : TEXT open WRITE_MODE is "../output/{evaluator_name}/sim/results_{evaluator_name}.txt";

begin

    uut : entity work.{evaluator_name}
        generic map (
            DATA_WIDTH => {data_width}{f",\n\t\t\tSEGMENT_IDX_WIDTH => {segment_idx_width}" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{f",\n\t\t\tGROUP_IDX_WIDTH => {group_idx_width}" if evaluator_type == "binary" else ""}
        )
        port map (
            input_a => input_a,
            result  => result
        );

    tb_proc: process
        variable line_out : line;
        variable input_str, result_str : string(1 to {data_width});
    begin
        for i in 0 to 2**{data_width} - 1 loop
            input_a <= std_logic_vector(to_unsigned(i, {data_width}));

            wait for 10 ns;

            write(line_out, integer'image(i));
            write(line_out, string'(","));
            write(line_out, integer'image(to_integer(unsigned(result))));
            writeline(output_file, line_out);

        end loop;
        
        std.env.stop(0);
    end process;

end arch_tb_{evaluator_name};
"""
