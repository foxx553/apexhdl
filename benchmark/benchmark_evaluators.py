import subprocess
import re
import math
import time

def parse_utilization_report(filepath):
    """ Parse a Vivado utilization report and return the 'Total LUTs' value for the 'uut' instance. """
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip().startswith('| top'):
                parts = [p.strip() for p in line.split('|')]
                return int(parts[3])

def parse_timing_report(filepath):
    """ Parse a Vivado timing report and return the first 'Data Path Delay' value in nanoseconds. """
    with open(filepath, 'r') as file:
        content = file.read()
        match = re.search(r"Data Path Delay:\s+([\d.]+)ns", content)
        if match:
            return float(match.group(1))

def parse_results_file(filepath):
    """ Parse the results file to get max and mean errors """
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
        second_last_line = lines[-2]
        parts = second_last_line.split(',')
        max_error, mean_error = map(float, parts)
        last_line = lines[-1]
        parts = last_line.split(',')
        max_relative_error, mean_relative_error = map(float, parts)
        return max_error, mean_error, max_relative_error, mean_relative_error

def benchmark_module(run_mode, params):
    """ Launches the benchmark of one module """

    # Launch generation of VHDL module & its metrics
    cmd = ["python", "../generation/generate_evaluator.py"] + params + ["--rpt" if run_mode == "impl" else "--rpt-synth"]
    print(f"Running cmd {cmd}...")
    subprocess.run(cmd, capture_output=True, check=True)

    # Args extraction
    evaluator_type, evaluator_name, function_of_x, data_width, x_min, x_max, y_min, y_max = params[:8]
    segment_idx_width = params[8] if len(params) > 8 else None
    group_idx_width = params[9] if len(params) > 9 else None

	# Reports parsing
    area = parse_utilization_report(f"../output/{evaluator_name}/rpt/{evaluator_name}_utilization.rpt") if run_mode == "impl" else parse_utilization_report(f"../output/{evaluator_name}/rpt/{evaluator_name}_synth_utilization.rpt")
    latency = parse_timing_report(f"../output/{evaluator_name}/rpt/{evaluator_name}_timing.rpt") if run_mode == "impl" else ""
    max_error, mean_error, max_relative_error, mean_relative_error = parse_results_file(f"../output/{evaluator_name}/sim/results_{evaluator_name}.txt")

    return f"{evaluator_type}; {evaluator_name}; {function_of_x}; {data_width}; {x_min}; {x_max}; {y_min}; {y_max}; {segment_idx_width or ""}; {group_idx_width or ""}; {area}; {latency}; {max_error}; {mean_error}; {max_relative_error}; {mean_relative_error};\n"


def main():
    """ Launches the full benchmark on the provided set of parameters """
    
    # add_header = True
    # benchmark_name = "001"
    # run_mode = "synth"
    # methods = ["symmetric", "binary", "rom", "hybrid"]
    # precisions = [8, 10, 12, 14, 16]
    # functions = [
    #     ["sin_low_freq", "\"sin(x*pi)\"", -1, 1, -1.1, 1.1],
    #     ["sin_high_freq", "\"sin(5*x*pi)\"", -1, 1, -1.1, 1.1],
    #     ["gelu", "\"0.5*x*(1+tanh(sqrt(2/pi)*(x+0.044715*x**3)))\"", -3, 5, -0.3, 5.1],
    #     ["tanh", "\"128*tanh(0.03*(x-128))+128\"", 0, 256, 0, 256]
    # ]
    
    
    add_header = False
    benchmark_name = "001"
    run_mode = "synth"
    methods = ["unary"]
    precisions = [8, 10]
    functions = [
        ["sin_low_freq", "\"sin(x*pi)\"", -1, 1, -1.1, 1.1],
        ["sin_high_freq", "\"sin(5*x*pi)\"", -1, 1, -1.1, 1.1],
        ["gelu", "\"0.5*x*(1+tanh(sqrt(2/pi)*(x+0.044715*x**3)))\"", -3, 5, -0.3, 5.1],
        ["tanh", "\"128*tanh(0.03*(x-128))+128\"", 0, 256, 0, 256]
    ]

    sample_count = len(precisions) * len(methods) * len(functions)
    counter = 0
    if add_header:
        current_line = "type; name; function; data_width; x_min; x_max; y_min; y_max; segment_idx_width; group_idx_width; area (LUT); latency (ns); max_absolute_error; mean_absolute_error; max_relative_error; mean_relative_error;\n"
        with open(f"./results_bench_{benchmark_name}.csv", "a") as file:
            file.write(current_line)
    
    overall_start = time.time()
    print(f"Start benchmark at {time.strftime("%H:%M:%S")}")

    for evaluator_type in methods:
        for data_width in precisions:
            for function_set in functions:
                start = time.time()
                counter += 1
                evaluator_name = f"{evaluator_type}_{data_width}bit_{function_set[0]}"
                print(f"[{counter}/{sample_count}] Benchmarking {evaluator_name}...")
                if evaluator_type == "symmetric" or evaluator_type == "binary":
                    current_line = benchmark_module(run_mode, list(map(str, [evaluator_type, evaluator_name, function_set[1], data_width, function_set[2], function_set[3], function_set[4], function_set[5], math.ceil(data_width / 2), math.ceil(data_width / 4)])))
                elif evaluator_type == "hybrid":
                    current_line = benchmark_module(run_mode, list(map(str, [evaluator_type, evaluator_name, function_set[1], data_width, function_set[2], function_set[3], function_set[4], function_set[5], math.ceil(data_width / 2)])))
                else:
                    current_line = benchmark_module(run_mode, list(map(str, [evaluator_type, evaluator_name, function_set[1], data_width, function_set[2], function_set[3], function_set[4], function_set[5]])))
                with open(f"./results_bench_{benchmark_name}.csv", "a") as file:
                    file.write(current_line)
                end = time.time()
                print(f"[{counter}/{sample_count}] Successfully benchmarked {evaluator_name} at {time.strftime("%H:%M:%S")} after {end - start} seconds")
    
    overall_end = time.time()
    print(f"Start benchmark at {time.strftime("%H:%M:%S")} after {overall_end - overall_start} seconds")
        

if __name__ == "__main__":
    main()