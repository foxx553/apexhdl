from typing import Callable, Any, cast, no_type_check
from apex.context import Context
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sympy import symbols, sympify, lambdify, Expr # type: ignore

Predicate = Callable[[Context], bool]
"""
Alias for a boolean check on pipeline context
"""

THEORETICAL_STEP: float = 0.001
"""
Step considered for theoretical vs. experimental analysis
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
        expr: Expr = cast(Expr, sympify(function_str))
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
    x_float_values: list[float] = np.arange(x_min, x_max, x_step).tolist()

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
    
def write_apex_report(output_folder: Path, metrics: dict[str, float]):
    """
    Writes the ApexHDL report containing all metrics extracted during pipeline execution

    Parameters:
        output_folder (Path): Path to the folder containing the evaluator's artifacts
        metrics (dict[str, float]): Dictionary containing all metrics extracted
    """

    Path(output_folder / "apex_report.rpt").write_text("----------------------\nGenerated with ApexHDL\n----------------------\n\n" + "\n".join(f"{metric_name}: {metric_value}" for metric_name, metric_value in metrics.items()))

def create_benchmark_csv(output_folder: Path, benchmark_name: str):
    """
    Creates the benchmark CSV file, and writes the header in it

    Parameters:
        output_folder (Path): Path to the folder in which all benchmarks modules are put
        benchmark_name (str): Name of the benchmark
    """

    # Create folder if necessary
    output_folder.mkdir(parents=True, exist_ok=True)

    # Create benchmark CSV file
    file_path: Path = output_folder / f"{benchmark_name}.csv"
    file_path.write_text("----------------------\nGenerated with ApexHDL\n----------------------\n\n")

def append_benchmark_csv(output_folder: Path, benchmark_name: str, ctx: Context, metrics: dict[str, float], is_first: bool):
    """
    Appends the benchmark CSV file with the results of the current circuit

    Parameters:
        output_folder (Path): Path to the folder in which all benchmarks modules are put
        benchmark_name (str): Name of the benchmark
        ctx (Context): Context of the current circuit
        metrics (dict[str, float]): Metrics extracted
        is_first (bool): Whether a header needs to be added or not
    """

    # Get path to CSV file
    file_path: Path = output_folder / f"{benchmark_name}.csv"

    # Add a header if necessary
    if is_first:
        header: str = f"MethodName,CircuitName,MathFunction,DataWidth,XMin,XMax,YMin,YMax,SegmentIdxWidth,GroupIdxWidth,{",".join(f"{metric_name}" for metric_name, _ in metrics.items())}\n"
        with file_path.open('a') as file:
            file.write(header)

    # Add the current data
    current_line: str = f"{ctx.method_name},{ctx.circuit_name},{ctx.math_function},{ctx.data_width},{ctx.x_min},{ctx.x_max},{ctx.y_min},{ctx.y_max},{ctx.segment_idx_width},{ctx.group_idx_width},{",".join(f"{metric_value}" for _, metric_value in metrics.items())}\n"
    with file_path.open('a') as file:
        file.write(current_line)

# Note: Matplotlib hasn't fully typed its arguments. We thus disable type check for that specific function which uses Matplotlib for plotting ApexHDL graphs
@no_type_check
def generate_apex_plot(x_values: list[float], y_data: dict[str, tuple[list[float], str]], path: Path, title: str, subtitle: str, ylabel: str, xlabel: str = "Input"):
    """
    Generates a plot following ApexHDL format

    Parameters:
        x_values (list[float]): X values to be considered in the plot
        y_data (dict[str, tuple[list[float], str]]): Data to be plotted, with its associated color
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

def process_outputs_file(outputs_file: Path, dest_folder: Path, circuit_name: str, lambda_function: Any, data_width: int, x_min: float, x_max: float, y_min: float, y_max: float, is_simulation: bool) -> tuple[float, float, float, float]:
    """
    Generates the output plot and computes the approximation errors from the raw outputs CSV file

    Parameters:
        outputs_file (Path): Path of the raw CSV file
        dest_folder (Path): Target folder for the generated plots
        circuit_name (str): Name of the circuit
        lambda_function (Any): Mathematical function evaluated
        data_width (int): Number of bits of the approximation
        x_min (float): Minimum X value
        x_max (float): Maximum X value
        y_min (float): Minimum Y value
        y_max (float): Maximum Y value
        is_simulation (bool): Whether or not we are in simulation (or in on-chip validation)

    Returns:
        tuple[float, float, float, float]: Computed approximation errors (in the order: mean absolute error, max absolute error, mean relative error, max relative error)
    """

    # Validation parameters
    x_step: float = (x_max - x_min) / (2 ** data_width)
    y_step: float = (y_max - y_min) / (2 ** data_width)

    # Read outputs file
    raw_y_values: list[int] = []
    with outputs_file.open('r') as file:
        for line in file:
            parts: list[str] = line.strip().split(',')
            if len(parts) >= 2:
                raw_y_values.append(int(parts[1]))

    # Computing theoretical and experimental values
    x_values: list[float] = np.arange(x_min, x_max, THEORETICAL_STEP).tolist()
    y_evaluator: list[float] = []
    y_theoretical: list[float] = []
    absolute_errors: list[float] = []
    relative_errors: list[float] = []
    for x_value in x_values:
        theoretical: float = lambda_function(x_value)
        evaluator: float = y_min + raw_y_values[clamp_nearest(x_value, x_min, x_step, data_width)] * y_step
        y_theoretical.append(theoretical)
        y_evaluator.append(evaluator)
        absolute_errors.append(abs(theoretical - evaluator))
        relative_errors.append(0 if theoretical == 0 else abs((theoretical - evaluator) / theoretical))

    # Computing errors
    mean_absolute_error: float = float(np.mean(absolute_errors))
    max_absolute_error: float = np.max(absolute_errors)
    mean_relative_error: float = float(np.mean(relative_errors))
    max_relative_error: float = np.max(relative_errors)

    # Computing and saving comparison plot
    generate_apex_plot(
        x_values, 
        {
            "Theoretical": (y_theoretical, "blue"),
            "Experimental": (y_evaluator, "red")
        },
        dest_folder / f"curves_{circuit_name}.svg",
        "Theoretical vs. experimental",
        f"during {"simulation" if is_simulation else "on-chip validation"}",
        "Output"
    )

    # Computing and saving absolute error plot
    generate_apex_plot(
        x_values, 
        {
            "Errors": (absolute_errors, "blue"),
            f"Max = {"{:.3g}".format(max_absolute_error)}": ([max_absolute_error for _ in range(len(x_values))], "red"),
            f"Mean = {"{:.3g}".format(mean_absolute_error)}": ([mean_absolute_error for _ in range(len(x_values))], "orange")
        },
        dest_folder / f"error_absolute_{circuit_name}.svg",
        "Absolute errors",
        f"during {"simulation" if is_simulation else "on-chip validation"}",
        "Error"
    )

    # Computing and saving relative error plot
    generate_apex_plot(
        x_values, 
        {
            "Errors": (relative_errors, "blue"),
            f"Max = {"{:.3g}".format(max_relative_error)}": ([max_relative_error for _ in range(len(x_values))], "red"),
            f"Mean = {"{:.3g}".format(mean_relative_error)}": ([mean_relative_error for _ in range(len(x_values))], "orange")
        },
        dest_folder / f"error_relative_{circuit_name}.svg",
        "Relative errors",
        f"during {"simulation" if is_simulation else "on-chip validation"}",
        "Error"
    )

    # Returning errors
    return (mean_absolute_error, max_absolute_error, mean_relative_error, max_relative_error)