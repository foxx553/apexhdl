from utils import clamp_nearest, int_to_lsb
from sympy import symbols, sympify, lambdify
import numpy as np

def lut_method(args):
    
    # Args check
    if len(args) != 7:
        print("Usage: generate_evaluator.py lut <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>")
        return
    
    # Args extraction
    evaluator_name = args[0]
    data_width, x_min, x_max, y_min, y_max = map(int, args[2:7])

    # Function parsing
    x = symbols('x')
    function_of_x = args[1]
    try:
        expr = sympify(function_of_x)
        f = lambdify(x, expr, modules=['math'])
    except Exception as e:
        print("Failed to generate evaluator:")
        print(f"    >> Error parsing function: {e}")
        return

    # Function space discretization
    x_step = (x_max - x_min) / (2 ** data_width)
    y_step = (y_max - y_min) / (2 ** data_width)
    x_float_values = np.arange(x_min, x_max, x_step)

    # Function space computation
    y_float_values = [f(x) for x in x_float_values]
    y_discrete_values = [clamp_nearest(y, y_min, y_step, data_width) for y in y_float_values]

    # VHDL behavioral code generation
    behavioral_code = "\twith input_a select result <=\n"
    for x_value, y_value in enumerate(y_discrete_values):
        behavioral_code += f"\t\t\"{int_to_lsb(y_value, data_width)}\" when \"{int_to_lsb(x_value, data_width)}\",\n"
    behavioral_code += f"\t\t\"{int_to_lsb(0, data_width)}\" when others;"

    # VHDL complete code generation
    return f"""
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: {evaluator_name}
-- Function: f(x) = {function_of_x}
-- Evaluator method: LUT
-- Data width: {data_width} bits
-- Range: x in [{x_min};{x_max}[, y in [{y_min};{y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {evaluator_name} is
    generic (
        DATA_WIDTH : positive := {data_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {evaluator_name};

architecture arch_{evaluator_name} of {evaluator_name} is
begin

{behavioral_code}

end arch_{evaluator_name};
    """

def binary_method(args):
    return ""

def unary_method(args):
    return ""

def hybrid_method(args):
    return ""

# Evaluation methods mapping
evaluation_methods_map = {
    "lut": lut_method,
    "binary": binary_method,
    "unary": unary_method,
    "hybrid": hybrid_method
}   