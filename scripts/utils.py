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

def compute_relative_discrete_output(function_str, x_data_width, x_min, x_max, y_data_width, y_min, y_max, y_offset):
    """ Gets the discrete output array corresponding to a function into a discrete window, with a specific offset """

    # Gather absolute values
    absolute_values = compute_discrete_output(function_str, x_data_width, x_min, x_max, y_data_width, y_min, y_max)
    
    # Offset it by the bias
    relative_values = [y - clamp_nearest(y_offset, y_min, (y_max - y_min) / (2 ** y_data_width), y_data_width) for y in absolute_values]
    print(relative_values)
    return relative_values

def compute_unary_routing_logic(x_data_width, y_data_width, y_discrete_values):
    """ Generates unary core routing logic """
    
    # Computing routing logic
    unary_core_array = [[0 for _ in range(2**x_data_width)] for _ in range(2**y_data_width)]
    y_cursor = 0
    unary_core_array[0][0] = 1
    for x_value, y_value in enumerate(y_discrete_values):
        if y_value != y_cursor:
            step = 1 if y_value > y_cursor else -1
            for i in range(y_cursor + step, y_value + step, step):
                unary_core_array[i][x_value] = 1
            y_cursor = y_value

    return unary_core_array