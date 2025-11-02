from sympy import symbols, sympify, lambdify
import numpy as np

def parse_function(function_str):
    """ Parse a function of x string """

    x = symbols('x')
    function_of_x = function_str
    try:
        expr = sympify(function_of_x)
        return lambdify(x, expr, modules=['math'])
    except Exception as e:
        print("Failed to generate evaluator:")
        print(f"    >> Error parsing function: {e}")
        return

def clamp_nearest(value, window_min, window_step, window_bit_width):
    """ Clamp to nearest discrete value """

    float_quotient = (value - window_min) / window_step
    float_remainder = float_quotient % 1
    nearest_int = int(float_quotient) if float_remainder < 0.5 else int(float_quotient) + 1
    return max(0, min(nearest_int, 2 ** window_bit_width - 1))

def int_to_lsb(n, data_width):
    """ Gets the least significant bits of an integer """

    masked = n & ((2 ** data_width) - 1)
    return format(masked, f'0{data_width}b')

def compute_discrete_output(function_str, x_data_width, x_min, x_max, y_data_width, y_min, y_max):
    """ Gets the discrete output array corresponding to a function into a discrete window """

    # Function parsing
    f = parse_function(function_str)

    # Function space discretization
    x_step = (x_max - x_min) / (2 ** x_data_width)
    y_step = (y_max - y_min) / (2 ** y_data_width)
    x_float_values = np.arange(x_min, x_max, x_step)

    # Function space computation
    y_float_values = [f(x) for x in x_float_values]
    return [clamp_nearest(y, y_min, y_step, y_data_width) for y in y_float_values]

def generate_testbench(evaluator_type, args):
    """ Generates an exhaustive testbench for validation """

    # Args extraction
    evaluator_name = args[0]
    data_width = int(args[2])
    segment_idx_width, group_idx_width = 0, 0
    if evaluator_type == "binary":
        segment_idx_width, group_idx_width = int(args[7]), int(args[8]) 

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

    constant DATA_WIDTH : positive := {data_width};{f"\n\tconstant GROUP_IDX_WIDTH : positive := {group_idx_width};\n\tconstant SEGMENT_IDX_WIDTH : positive := {segment_idx_width};" if evaluator_type == "binary" else ""}

    signal input_a : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal result  : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);

    component {evaluator_name}
        generic (
            DATA_WIDTH : positive := {data_width}{f";\n\t\t\tGROUP_IDX_WIDTH : positive := {group_idx_width};\n\t\t\tSEGMENT_IDX_WIDTH : positive := {segment_idx_width}" if evaluator_type == "binary" else ""}
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
            DATA_WIDTH => DATA_WIDTH{",\n\t\t\tGROUP_IDX_WIDTH => GROUP_IDX_WIDTH,\n\t\t\tSEGMENT_IDX_WIDTH => SEGMENT_IDX_WIDTH" if evaluator_type == "binary" else ""}
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