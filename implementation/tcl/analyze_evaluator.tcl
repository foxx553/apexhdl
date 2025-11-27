# Get command line arguments for module name
set module_name [lindex $argv 0]
set run_mode [lindex $argv 1]

# Create in-memory project
create_project -in_memory -part xc7z020clg400-1

# Add source files
add_files ../output/${module_name}/vhdl/${module_name}.vhd
add_files ../output/${module_name}/vhdl/top_${module_name}.vhd
add_files ../implementation/xdc/timing_constraints.xdc

# Set-up VHDL-2008
set_property FILE_TYPE {VHDL 2008} [get_files -filter {FILE_TYPE == VHDL}]

# Set top module
set_property TOP top_${module_name} [current_fileset]

# Run synthesis
synth_design

if {$run_mode == "synth"} {
	
	# Generate post-synthesis utilization report
	report_utilization -hierarchical -file ../output/${module_name}/rpt/${module_name}_synth_utilization.rpt

} else {
	
	# Run implementation
	opt_design
	place_design
	route_design

	# Generate all post-implementation reports
	report_utilization -hierarchical -file ../output/${module_name}/rpt/${module_name}_utilization.rpt
	report_timing -max_paths 10 -delay_type min_max -sort_by group -file ../output/${module_name}/rpt/${module_name}_timing.rpt
	report_power -file ../output/${module_name}/rpt/${module_name}_power.rpt
	
}

# Close project
close_project