from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import shutil
import os
import subprocess

def generate_notebook(args):
    """ Generates Jupyter notebook for evaluator testing on PYNQ-Z2 """

    # Args extraction
    evaluator_name = args[0]
    data_width = int(args[2])
    x_min, x_max, y_min, y_max = map(float, args[3:7])

    # Notebook creation and title
    evaluator_notebook = new_notebook()
    evaluator_notebook.cells.append(new_markdown_cell(f"# {evaluator_name}"))

    # Write bitstream cells
    evaluator_notebook.cells.append(new_markdown_cell("# 1. Write bitstream"))
    evaluator_notebook.cells.append(new_code_cell(f"""
from pynq import Overlay

overlay = Overlay("./{evaluator_name}.bit")
"""))
    
    # GPIOs API cells
    evaluator_notebook.cells.append(new_markdown_cell("# 2. Create GPIOs API"))
    evaluator_notebook.cells.append(new_code_cell(f"""
from pynq import MMIO

axi_gpio_0_addr = 0x41200000
axi_gpio_1_addr = 0x41210000
axi_gpio_range = 0x10000
gpio_input_a = MMIO(axi_gpio_0_addr, axi_gpio_range)
gpio_result = MMIO(axi_gpio_1_addr, axi_gpio_range)

data_width, x_min, x_max, y_min, y_max = {data_width}, {x_min}, {x_max}, {y_min}, {y_max}
x_step = (x_max - x_min) / (2 ** data_width)
y_step = (x_max - x_min) / (2 ** data_width)

def write_input_a(value):
    gpio_input_a.write(0x0, int((value - x_min) / x_step))
def read_result():
    return y_min + gpio_result.read(0x0) * y_step
"""))
    
    # Testing cells
    evaluator_notebook.cells.append(new_markdown_cell("# 3. Play with it!"))
    evaluator_notebook.cells.append(new_code_cell(f"""
import math
import numpy as np

x_values = np.arange({x_min}, {x_max}, x_step)
y_evaluator = []

for x_value in x_values:
    write_input_a(x_value)
    evaluator = read_result()
    y_evaluator.append(evaluator)
"""))
    evaluator_notebook.cells.append(new_code_cell(f"""
import matplotlib.pyplot as plt

plt.figure(figsize=(20, 10))
plt.plot(x_values, y_evaluator, color='red', linewidth=1)
plt.title('Experimental values')
plt.xlabel('x')
plt.ylabel('Values')
plt.grid(True)
plt.show()
"""))

    return evaluator_notebook

def run_vivado_implementation(evaluator_name, data_width):
    """Run Vivado TCL script and capture results"""
    
    # Vivado execution in batch mode
    cmd = [
        "vivado",
        "-mode", "batch",
        "-source", "../implementation/tcl/implement_evaluator.tcl",
        "-tclargs", evaluator_name, str(data_width)
    ]
    result = subprocess.run(cmd, shell=True, text=True)
    if os.path.exists(f"../output/{evaluator_name}/bit/vivado.log"):
        os.remove(f"../output/{evaluator_name}/bit/vivado.log")
    shutil.move("vivado.log", f"../output/{evaluator_name}/bit/")
    
    if result.returncode != 0:
        print(f"Error running Vivado for {evaluator_name}:")
        print(result.stderr)
        return None