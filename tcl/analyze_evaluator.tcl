# Get command line arguments
set fpga_board [lindex $argv 0]
set output_folder [lindex $argv 1]
set module_name [lindex $argv 2]
set run_mode [lindex $argv 3]

# Create in-memory project
create_project -in_memory -part ${fpga_board}

# Add source files
add_files ${output_folder}/${module_name}/vhdl/${module_name}.vhd
add_files ${output_folder}/${module_name}/vhdl/top_${module_name}.vhd

# Add virtual clock constraint file
add_files ../xdc/virtual_clk.xdc

# Set-up VHDL-2008
set_property FILE_TYPE {VHDL 2008} [get_files -filter {FILE_TYPE == VHDL}]

# Set top module
set_property TOP top_${module_name} [current_fileset]

# Run synthesis
synth_design

if {$run_mode == "syn"} {
	
	# Generate post-synthesis utilization report
	report_utilization -hierarchical -file ${output_folder}/${module_name}/syn/${module_name}_utilization.rpt

} else {
	
	# Run place-and-route
	opt_design
	place_design
	route_design

	# Generate all post-place-and-route reports
	report_utilization -hierarchical -file ${output_folder}/${module_name}/syn/${module_name}_utilization.rpt
	report_timing -max_paths 10 -delay_type min_max -sort_by group -file ${output_folder}/${module_name}/syn/${module_name}_timing.rpt
	report_power -file ${output_folder}/${module_name}/syn/${module_name}_power.rpt
	
}

# Close project
close_project