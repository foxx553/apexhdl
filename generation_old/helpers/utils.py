from sympy import symbols, sympify, lambdify
import numpy as np
import os
import zipfile

def extract_hwh_from_xsa(xsa_file_path, hwh_file_name):
    """ Extract HWH file from XSA archive """

    output_dir = os.path.dirname(xsa_file_path)
    
    with zipfile.ZipFile(xsa_file_path, 'r') as xsa_zip:
        
        # Finding HWH file among XSA files
        file_list = xsa_zip.namelist()
        hwh_files = [file for file in file_list if file.endswith('.hwh')]
        
        # Extract HWH file
        filename = hwh_files[0]
        xsa_zip.extract(filename, output_dir)
        
        # Rename the extracted file to the desired name
        extracted_file_path = os.path.join(output_dir, filename)
        final_file_path = os.path.join(output_dir, hwh_file_name)
        
        # Remove target if it exists, then rename
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
        os.rename(extracted_file_path, final_file_path)
    
    # Remove the XSA archive
    os.remove(xsa_file_path)
    
    return

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

    nbr_steps_from_min = (value - window_min) / window_step
    float_remainder = nbr_steps_from_min % 1
    nearest_int = int(nbr_steps_from_min) if float_remainder < 0.5 else int(nbr_steps_from_min) + 1
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
