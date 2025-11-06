create_clock -name virt_clk -period 5.0

set_input_delay -clock virt_clk -max 0 [get_ports input_a]
set_input_delay -clock virt_clk -min 0 [get_ports input_a]
 
set_output_delay -clock virt_clk -max 0 [get_ports result]
set_output_delay -clock virt_clk -min 0 [get_ports result]