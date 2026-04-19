from typing import Callable, Any
from apex.context import Context
from sympy import symbols, sympify, lambdify
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

Predicate = Callable[[Context], bool]
"""
Alias for a boolean check on pipeline context
"""

def lambdify_function(function_str: str) -> Any:
    """
    Lambdifies a mathematical function from a string 
    
    Parameters:
        function_str (str): String of the function to be parsed
    
    Returns:
        Any: Lambda function
    """

    x: Any = symbols('x')
    try:
        expr: Any = sympify(function_str)
        return lambdify(x, expr, modules=['math'])
    except Exception as e:
        raise RuntimeError(f"Failed mathematical function lambdification: {e}")

def clamp_nearest(value: float, window_min: float, window_step: float, window_bit_width: int) -> int:
    """
    Clamps a real value to its discrete step count in a discrete window

    Parameters:
        value (float): Real value to be discretized
        window_min (float): Minimum real value of the discrete window
        window_step (float): Real value of the discrete window step
        window_bit_width (int): Number of bits of the discrete window
    
    Returns:
        int: Integer value in the discrete window
    """

    nbr_steps_from_min: float = (value - window_min) / window_step
    float_remainder: float = nbr_steps_from_min % 1
    nearest_int: int = int(nbr_steps_from_min) if float_remainder < 0.5 else int(nbr_steps_from_min) + 1
    return max(0, min(nearest_int, 2 ** window_bit_width - 1))

def int_to_lsb(n: int, data_width: int) -> str:
    """
    Gets the LSBs (Least Significant Bits) of an integer

    Parameters:
        n (int): Integer value
        data_width (int): Number of LSBs wanted
    
    Returns:
        str: LSBs extracted
    """

    masked: int = n & ((2 ** data_width) - 1)
    return format(masked, f'0{data_width}b')

def compute_discrete_output(function_str: str, x_data_width: int, x_min: float, x_max: float, y_data_width: int, y_min: float, y_max: float) -> list[int]:
    """
    Applies a discrete window to a mathematical function. For each value of the discrete x axis, applies the mathematical function, and clamps the output onto the discrete y axis

    Parameters:
        function_str (str): String of the function to be parsed
        x_data_width (int): Number of bits of the discrete x axis
        x_min (float): Minimum value of the discrete x axis
        x_max (float): Maximum value of the discrete x axis
        y_data_width (int): Number of bits of the discrete y axis
        y_min (float): Minimum value of the discrete y axis
        y_max (float): Maximum value of the discrete y axis
    
    Returns:
        list[int]: Outputs of the mathematical function in the discretized space
    """

    # Function lambdify
    f: Any = lambdify_function(function_str)

    # Function space discretization
    x_step: float = (x_max - x_min) / (2 ** x_data_width)
    y_step: float = (y_max - y_min) / (2 ** y_data_width)
    x_float_values: list[float] = np.arange(x_min, x_max, x_step)

    # Function space computation
    y_float_values: list[float] = [f(x) for x in x_float_values]
    return [clamp_nearest(y, y_min, y_step, y_data_width) for y in y_float_values]

def compute_relative_discrete_output(function_str: str, x_data_width: int, x_min: float, x_max: float, y_data_width: int, y_min: float, y_max: float, y_origin: float) -> list[int]:
    """
    Applies a discrete window to a mathematical function, and returns the signed value relative to a certain origin (e.g. '0' for computing a relative offset). For each value of the discrete x axis, applies the mathematical function, clamps the output onto the discrete y axis, and offsets it by the discrete value of the origin float

    Parameters:
        
    Parameters:
        function_str (str): String of the function to be parsed
        x_data_width (int): Number of bits of the discrete x axis
        x_min (float): Minimum value of the discrete x axis
        x_max (float): Maximum value of the discrete x axis
        y_data_width (int): Number of bits of the discrete y axis
        y_min (float): Minimum value of the discrete y axis
        y_max (float): Maximum value of the discrete y axis
        y_origin (float): Origin float
    
    Returns:
        list[int]: Outputs of the mathematical function in the relative discretized space
    """

    # Gather absolute values
    absolute_values: list[int] = compute_discrete_output(function_str, x_data_width, x_min, x_max, y_data_width, y_min, y_max)
    
    # Offset it by the bias
    return [y - clamp_nearest(y_origin, y_min, (y_max - y_min) / (2 ** y_data_width), y_data_width) for y in absolute_values]
    
def create_benchmark_csv(output_folder: Path, benchmark_name: str):
    """
    Creates the benchmark CSV file, and writes the header in it

    Parameters:
        output_folder (Path): Path to the folder in which all benchmarks modules are put
        benchmark_name (str): Name of the benchmark
    """

    # Create folder if necessary
    output_folder.mkdir(parents=True, exist_ok=True)

    # Create header
    header: str = "method_name,circuit_name,math_function,data_width,x_min,x_max,y_min,y_max,segment_idx_width,group_idx_width,max_absolute_error,mean_absolute_error,max_relative_error,mean_relative_error,lut,latency,\n"

    # Create benchmark CSV file
    file_path: Path = output_folder / f"{benchmark_name}.csv"
    file_path.write_text(header)

def append_benchmark_csv(output_folder: Path, benchmark_name: str, ctx: Context):
    """
    Appends the benchmark CSV file with the results of the current circuit

    Parameters:
        output_folder (Path): Path to the folder in which all benchmarks modules are put
        benchmark_name (str): Name of the benchmark
        ctx (Context): Context of the current circuit
    """

    # Get path to CSV file
    file_path: Path = output_folder / f"{benchmark_name}.csv"

    # Parse simulation results, if the file exists
    simulation_file_path: Path = output_folder / ctx.circuit_name / "sim" / f"results_{ctx.circuit_name}.txt"
    max_absolute_error, mean_absolute_error, max_relative_error, mean_relative_error = None, None, None, None
    if simulation_file_path.exists():
        with simulation_file_path.open('r') as file:
            lines: list[str] = [line.strip() for line in file if line.strip()]
            max_absolute_error, mean_absolute_error = map(float, lines[-2].split(','))
            max_relative_error, mean_relative_error = map(float, lines[-1].split(','))

    # Parse utilization report, if the file exists
    utilization_file_path: Path = output_folder / ctx.circuit_name / "syn" / f"{ctx.circuit_name}_utilization.rpt"
    lut = None
    if utilization_file_path.exists():
        with utilization_file_path.open('r') as file:
            for line in file:
                if line.strip().startswith('| top'):
                    parts = [p.strip() for p in line.split('|')]
                    lut = int(parts[3])
    
    # Parse timing report, if the file exists
    timing_file_path: Path = output_folder / ctx.circuit_name / "syn" / f"{ctx.circuit_name}_timing.rpt"
    latency = None
    if timing_file_path.exists():
        with timing_file_path.open('r') as file:
            content = file.read()
            match = re.search(r"Data Path Delay:\s+([\d.]+)ns", content)
            if match:
                latency = float(match.group(1))

    # Create current line
    current_line: str = f"{ctx.method_name},{ctx.circuit_name},{ctx.math_function},{ctx.data_width},{ctx.x_min},{ctx.x_max},{ctx.y_min},{ctx.y_max},{ctx.segment_idx_width},{ctx.group_idx_width},{max_absolute_error},{mean_absolute_error},{max_relative_error},{mean_relative_error},{lut},{latency},\n"

    # Append current line to benchmark CSV file
    with file_path.open('a') as file:
        file.write(current_line)

def generate_apex_plot(x_values: list[float], y_data: dict[str, (list[float], str)], path: Path, title: str, subtitle: str, ylabel: str, xlabel: str = "Input"):
    """
    Generates a plot following ApexHDL format

    Parameters:
        x_values (list[float]): X values to be considered in the plot
        y_data (dict[str, (list[float], str)]): Data to be plotted, with its associated color
        path (Path): File path for the plot
        title (str): Title of the plot
        subtitle (str): Subtitle of the plot
        ylabel (str): Title of the Y axis
        xlabel (str): Title of the X axis
    """

    # Display parameters
    PLOT_WIDTH = 30
    PLOT_HEIGHT = 20
    LINE_WIDTH = 9
    GRID_WIDTH = 4.0
    FRAME_WIDTH = 7.0
    NOMINAL_FONT_SIZE = 60

    # Defining plot overall structure
    plt.figure(figsize=(PLOT_WIDTH, PLOT_HEIGHT))
    plt.suptitle(title, fontsize=NOMINAL_FONT_SIZE + 20, fontweight='bold')
    plt.title(subtitle, fontsize=NOMINAL_FONT_SIZE - 10, pad=20)
    plt.grid(True, linewidth=GRID_WIDTH, color='gray', alpha=0.5)
    plt.xlabel(xlabel, fontsize=NOMINAL_FONT_SIZE + 10)
    plt.ylabel(ylabel, fontsize=NOMINAL_FONT_SIZE + 10, labelpad=10)
    plt.xticks(fontsize=NOMINAL_FONT_SIZE)
    plt.yticks(fontsize=NOMINAL_FONT_SIZE)

    # Using axes to perform more precise customizations
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_linewidth(FRAME_WIDTH)
        spine.set_edgecolor('black')
    ax.tick_params(width=FRAME_WIDTH)
    ax.text(1.07, 0.5, "Generated with ApexHDL", transform=ax.transAxes, rotation=270, va='center', ha='left', fontsize=NOMINAL_FONT_SIZE, color='gray', alpha=0.6)

    # Plotting the data
    for name, (data_values, color) in y_data.items():
        plt.plot(x_values, data_values, color=color, linewidth=LINE_WIDTH, label=name)
    
    # Putting the legend
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=len(y_data), prop={'weight': 'bold', 'size': NOMINAL_FONT_SIZE}, frameon=False)

    # Saving the plot
    plt.savefig(path, format='svg', facecolor='white', transparent=False, bbox_inches='tight')

def insert_header(path: Path, header: str):
    """
    Insert header in file

    Parameters:
        path (Path): Path of the target file
        header (str): Header to be inserted at the beginning
    """

    content = path.read_text()
    path.write_text(header + content)