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
    x_min, x_max, y_min, y_max = map(float, args[3:7])

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
-- Engineer: Florian Delhon
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

    constant DATA_WIDTH : positive := {data_width};{f"\n\tconstant SEGMENT_IDX_WIDTH : positive := {segment_idx_width};" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{f"\n\tconstant GROUP_IDX_WIDTH : positive := {group_idx_width};" if evaluator_type == "binary" else ""}

    signal input_a : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal result  : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);

    component {evaluator_name}
        generic (
            DATA_WIDTH : positive := {data_width}{f";\n\t\t\tSEGMENT_IDX_WIDTH : positive := {segment_idx_width}" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{f";\n\t\t\tGROUP_IDX_WIDTH : positive := {group_idx_width}" if evaluator_type == "binary" else ""}
        );
        port (
            input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
            result  : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
        );
    end component;

    file output_file : TEXT open WRITE_MODE is "../sources/{evaluator_name}/results_{evaluator_name}.txt";

begin

    uut: {evaluator_name}
        generic map (
            DATA_WIDTH => DATA_WIDTH{",\n\t\t\tSEGMENT_IDX_WIDTH => SEGMENT_IDX_WIDTH" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{",\n\t\t\tGROUP_IDX_WIDTH => GROUP_IDX_WIDTH" if evaluator_type == "binary" else ""}
        )
        port map (
            input_a => input_a,
            result  => result
        );

    tb_proc: process
        variable line_out : line;
        variable input_str, result_str : string(1 to DATA_WIDTH);
    begin
        for i in 0 to 2**DATA_WIDTH - 1 loop
            input_a <= std_logic_vector(to_unsigned(i, DATA_WIDTH));

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
