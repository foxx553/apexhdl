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

def compute_discrete_output(function_str, data_width, x_min, x_max, y_min, y_max):
    """ Gets the discrete output array corresponding to a function into a discrete window """

    # Function parsing
    f = parse_function(function_str)

    # Function space discretization
    x_step = (x_max - x_min) / (2 ** data_width)
    y_step = (y_max - y_min) / (2 ** data_width)
    x_float_values = np.arange(x_min, x_max, x_step)

    # Function space computation
    y_float_values = [f(x) for x in x_float_values]
    return [clamp_nearest(y, y_min, y_step, data_width) for y in y_float_values]