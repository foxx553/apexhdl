from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import shutil
import os
import subprocess

def generate_notebook(args):
    """ Generates Jupyter notebook for evaluator testing on PYNQ-Z2 """

    # Args extraction
    evaluator_name = args[0]
    function_str = args[1]
    data_width = int(args[2])
    x_min, x_max, y_min, y_max = map(float, args[3:7])
    is_image_processing_compatible = data_width, x_min, x_max, y_min, y_max == 8, 0, 256, 0, 256

    # Notebook creation and title
    evaluator_notebook = new_notebook()
    evaluator_notebook.cells.append(new_markdown_cell(f"# {evaluator_name}"))

    # Bitstream cells
    evaluator_notebook.cells.append(new_markdown_cell("# 1. Bitstream"))
    evaluator_notebook.cells.append(new_code_cell(f"""
# Imports
from pynq import Overlay
from pynq import allocate
from pynq import PL
import math
import numpy as np
import matplotlib.pyplot as plt

# Bitstream
PL.reset()
overlay = Overlay("./{evaluator_name}.bit")

# AXI-Stream
dma = overlay.axi_dma_0
dma_send = dma.sendchannel
dma_recv = dma.recvchannel

"""))
    
	# Function evaluation cells
    evaluator_notebook.cells.append(new_markdown_cell("# 2. Function evaluation"))
    evaluator_notebook.cells.append(new_code_cell(f"""
# Additional imports
from sympy import symbols, sympify, lambdify

# Function string
function_str = "{function_str}"

# Function parsing
x = symbols('x')
function_expr = sympify(function_str)
numpy_function = lambdify(x, function_expr, modules=['numpy'])
"""))
    
	# Mathematical test cells
    evaluator_notebook.cells.append(new_markdown_cell("# 3. Mathematical test"))
    evaluator_notebook.cells.append(new_code_cell(f"""
# Evaluator parameters
data_width, x_min, x_max, y_min, y_max = {data_width}, {x_min}, {x_max}, {y_min}, {y_max}
x_step = (x_max - x_min) / (2 ** data_width)
y_step = (x_max - x_min) / (2 ** data_width)

# Conversion methods
def convert_x_to_discrete_vectorized(x_vector):
    float_quotient = (x_vector - x_min) / x_step
    float_remainder = float_quotient % 1
    nearest_int = np.where(float_remainder < 0.5, np.floor(float_quotient), np.floor(float_quotient) + 1)
    return np.clip(nearest_int, 0, 2 ** data_width - 1).astype(np.uint16)
def convert_y_to_real_vectorized(y_vector):
    return y_min + y_vector * y_step

# X values
x_real_values = np.arange(x_min, x_max, 0.001)
x_discrete_values = allocate(shape=(len(x_real_values),), dtype=np.uint16)
discrete_result = convert_x_to_discrete_vectorized(x_real_values)
np.copyto(x_discrete_values, discrete_result)

# Y theoretical values
y_theoretical_values = numpy_function(x_real_values).astype(np.float32)

# Y experimental values
y_discrete_values = allocate(shape=(len(x_real_values),), dtype=np.uint16)
dma_send.transfer(x_discrete_values)
dma_recv.transfer(y_discrete_values)
dma_recv.wait()
y_experimental_values = convert_y_to_real_vectorized(y_discrete_values)

# Error computation
y_absolute_errors = np.abs(y_theoretical_values - y_experimental_values)
max_absolute_error = np.max(y_absolute_errors)
mean_absolute_error = np.mean(y_absolute_errors)
"""))
    evaluator_notebook.cells.append(new_code_cell(f"""
# Plot comparison theoretical vs. experimental
plt.figure(figsize=(20, 10))
plt.plot(x_real_values, y_theoretical_values, color='blue', linewidth=1, label='Theoretical values')
plt.plot(x_real_values, y_experimental_values, color='red', linewidth=1, label='Experimental values')
plt.title('Theoretical values vs. experimental values')
plt.xlabel('x')
plt.ylabel('Values')
plt.grid(True)
plt.legend(loc='upper center', bbox_to_anchor=(1, 0.5))
plt.show()
"""))
    evaluator_notebook.cells.append(new_code_cell("""
# Plot absolute error
plt.figure(figsize=(20, 10))
plt.plot(x_real_values, y_absolute_errors, color='blue', linewidth=1, label="Absolute errors")
plt.plot(x_real_values, [max_absolute_error for _ in range(len(x_real_values))], color='red', linewidth=2, label=f"Max error = {max_absolute_error:.3g}")
plt.plot(x_real_values, [mean_absolute_error for _ in range(len(x_real_values))], color='orange', linewidth=2, label=f"Mean error = {mean_absolute_error:.3g}")
plt.title('Absolute error of evaluator values')
plt.xlabel('x')
plt.ylabel('Absolute error')
plt.grid(True)
plt.legend(loc='upper center', bbox_to_anchor=(1, 0.5))
plt.show()
"""))
    
    if is_image_processing_compatible:
        
		# Image to be processed
        shutil.copy("../resources/img.jpg", f"../output/{evaluator_name}/bit/img.jpg")
        
        # Image processing cells
        evaluator_notebook.cells.append(new_markdown_cell("# 4. Use case: Image processing"))
        evaluator_notebook.cells.append(new_code_cell("""
# Additional imports
import cv2
import time

# Image reading
input_image = cv2.imread("./img.jpg", cv2.IMREAD_GRAYSCALE)
height, width = input_image.shape
print("= Input =")
print(f"> Resolution: {width}x{height}")
print("> Image:")
plt.imshow(input_image, cmap='gray')
plt.axis('off')
plt.show()

# Buffers
flatten_input = allocate(shape=(height*width,), dtype=np.uint16)
flatten_output_hw = allocate(shape=(height*width,), dtype=np.uint16)
np.copyto(flatten_input, input_image.flatten())

# Software processing using the function from string
start_time = time.perf_counter()
flatten_output_sw = numpy_function(flatten_input.astype(np.float32)).astype(np.uint16)
end_time = time.perf_counter()
sw_time = end_time - start_time
# --
print("= Software processing =")
print(f"> Time: {sw_time} seconds")
print("> Image:")
output_image_sw = flatten_output_sw.reshape(input_image.shape)
plt.imshow(output_image_sw, cmap='gray')
plt.axis('off')
plt.show()

# Hardware processing
start_time = time.perf_counter()
dma_send.transfer(flatten_input)
dma_recv.transfer(flatten_output_hw)
dma_recv.wait()
end_time = time.perf_counter()
hw_time = end_time - start_time
# --
print("= Hardware processing =")
print(f"> Time: {hw_time} seconds")
print("> Image:")
output_image_hw = flatten_output_hw.reshape(input_image.shape)
plt.imshow(output_image_hw, cmap='gray')
plt.axis('off')
plt.show()

# Acceleration computation
print("= Resulting acceleration =")
print(f"> Value: {sw_time/hw_time}")
"""))

    return evaluator_notebook

def run_vivado_implementation(evaluator_name):
    """Run Vivado TCL script and capture results"""

    # Vivado execution in batch mode
    cmd = [
        "vivado",
        "-mode", "batch",
        "-source", "../implementation/tcl/implement_evaluator.tcl",
        "-tclargs", evaluator_name
    ]
    result = subprocess.run(cmd, shell=True, text=True)
    if os.path.exists(f"../output/{evaluator_name}/bit/vivado.log"):
        os.remove(f"../output/{evaluator_name}/bit/vivado.log")
    shutil.move("vivado.log", f"../output/{evaluator_name}/bit/")
    
    if result.returncode != 0:
        print(f"Error running Vivado for {evaluator_name}:")
        print(result.stderr)
        return None
    
def generate_stream_top(evaluator_type, args):
    """ Generates the top module which wraps evaluator into AXI-Stream interface """

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
-- Engineers: Florian Delhon, Kevin Peymani
-- Target: PYNQ-Z2
-- Module Name: stream_top_{evaluator_name}
-- Description: AXI-Stream top module for {evaluator_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity stream_top_{evaluator_name} is
    port (
        din_tdata 	: in STD_LOGIC_VECTOR(15 downto 0);
        din_tlast 	: in STD_LOGIC;
        din_tvalid 	: in STD_LOGIC;
        din_tready 	: out STD_LOGIC;
        dout_tdata 	: out STD_LOGIC_VECTOR(15 downto 0);
        dout_tlast 	: out STD_LOGIC;
        dout_tvalid	: out STD_LOGIC;
        dout_tready : in STD_LOGIC;
		clk 		: in STD_LOGIC;
		rstn		: in STD_LOGIC
    );
end stream_top_{evaluator_name};

architecture arch_stream_top_{evaluator_name} of stream_top_{evaluator_name} is

	signal reg_tdata_in 	: STD_LOGIC_VECTOR({data_width - 1} downto 0);
	signal reg_tvalid_out 	: STD_LOGIC;
	signal reg_en 			: STD_LOGIC;

begin

    uut : entity work.{evaluator_name}
        generic map (
            DATA_WIDTH => {data_width}{f",\n\t\t\tSEGMENT_IDX_WIDTH => {segment_idx_width}" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{f",\n\t\t\tGROUP_IDX_WIDTH => {group_idx_width}" if evaluator_type == "binary" else ""}
        )
        port map (
            input_a => din_tdata({data_width - 1} downto 0),
            result  => reg_tdata_in
        );

	reg_tdata : process(clk, rstn)
	begin
		if rstn = '0' then
			dout_tdata <= (others => '0');
		elsif rising_edge(clk) then
			if reg_en = '1' then
				dout_tdata <= (others => '0');
				dout_tdata({data_width - 1} downto 0) <= reg_tdata_in;
			end if;
		end if;
	end process reg_tdata; 

	reg_tlast : process(clk, rstn)
	begin
		if rstn = '0' then
			dout_tlast <= '0';
		elsif rising_edge(clk) then
			if reg_en = '1' then
				dout_tlast <= din_tlast;
			end if;
		end if;
	end process reg_tlast;

	reg_tvalid : process(clk, rstn)
	begin
		if rstn = '0' then
			reg_tvalid_out <= '0';
		elsif rising_edge(clk) then
			if reg_en = '1' then
				reg_tvalid_out <= din_tvalid;
			end if;
		end if;
	end process reg_tvalid; 

	dout_tvalid <= reg_tvalid_out;
	reg_en <= dout_tready or not reg_tvalid_out;
	din_tready <= reg_en;
	
end arch_stream_top_{evaluator_name};
"""