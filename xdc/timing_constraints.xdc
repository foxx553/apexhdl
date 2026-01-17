# Create a virtual clock with a unreachable period (5 ns)
create_clock -name virt_clk -period 5.0

# Assume data is immediately stable at the input pin (T = 0 ns)
set_input_delay -clock virt_clk -max 0 [get_ports input_a]
set_input_delay -clock virt_clk -min 0 [get_ports input_a]
 
# Assume the output pin is captured at T = 5 ns
set_output_delay -clock virt_clk -max 0 [get_ports result]
set_output_delay -clock virt_clk -min 0 [get_ports result]