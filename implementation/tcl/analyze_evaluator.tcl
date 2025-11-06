# analyze_module.tcl
set module_name [lindex $argv 0]
set data_width [lindex $argv 1]

# Create in-memory project
create_project -in_memory -part xc7z020clg400-1

# Add source files
add_files ../output/${module_name}/vhdl/${module_name}.vhd
add_files ../output/${module_name}/vhdl/top_${module_name}.vhd
add_files ../implementation/xdc/timing_constraints.xdc

# Set top module
set_property TOP top_${module_name} [current_fileset]

# Run synthesis
synth_design

# Generate reports
report_timing -max_paths 10 -delay_type min_max -sort_by group -file ../output/${module_name}/rpt/${module_name}_timing.rpt
report_utilization -hierarchical -file ../output/${module_name}/rpt/${module_name}_utilization.rpt
report_power -file ../output/${module_name}/rpt/${module_name}_power.rpt

# Close project
close_project