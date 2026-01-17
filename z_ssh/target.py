# Imports
from pynq import Overlay
from pynq import allocate
from pynq import PL
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, lambdify

# Bitstream
PL.reset()
overlay = Overlay("./design.bit")

# AXI-Stream
dma = overlay.axi_dma_0
dma_send = dma.sendchannel
dma_recv = dma.recvchannel

# Function string
function_str = "200*exp(-(x-128)**2/(2*30**2))"

# Function parsing
x = symbols('x')
function_expr = sympify(function_str)
numpy_function = lambdify(x, function_expr, modules=['numpy'])


# Evaluator parameters
data_width, x_min, x_max, y_min, y_max = 8, 0.0, 256.0, 0.0, 256.0
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

# Plot comparison theoretical vs. experimental
plt.figure(figsize=(20, 10))
plt.plot(x_real_values, y_theoretical_values, color='blue', linewidth=3, label='Theoretical values')
plt.plot(x_real_values, y_experimental_values, color='red', linewidth=3, label='Experimental values')
plt.title('Theoretical values vs. experimental values', fontsize=30)
plt.xlabel('x', fontsize=28)
plt.ylabel('Values', fontsize=28)
plt.grid(True)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
plt.savefig("output.png")
