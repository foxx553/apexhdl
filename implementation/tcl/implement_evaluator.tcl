# Get command line arguments for module name and GPIO width
set module_name [lindex $argv 0]
set gpio_width [lindex $argv 1]

# Create in-memory project for faster processing
create_project -in_memory -part xc7z020clg400-1

# Add VHDL source and constraints files
add_files ../output/${module_name}/vhdl/${module_name}.vhd
add_files ../implementation/xdc/pynq-z2-template.xdc

# Set top module and update compilation order
set_property TOP ${module_name} [current_fileset]
set_property source_mgmt_mode All [current_project]
update_compile_order -fileset sources_1

# Create block design using custom wrapper script
source ../implementation/tcl/wrap_evaluator.tcl
update_compile_order -fileset sources_1
create_root_design "" $gpio_width $module_name
save_bd_design
validate_bd_design

# Generate all targets from block design
set bd_file [get_files *.bd]
generate_target all $bd_file

# Create and add wrapper for the block design
make_wrapper -files [get_files $bd_file] -top
add_files -norecurse ../generation/.gen/sources_1/bd/evaluator/hdl/evaluator_wrapper.v
update_compile_order -fileset sources_1

# Set wrapper as top module
set_property TOP evaluator_wrapper [current_fileset]
update_compile_order -fileset sources_1

# Run full implementation flow
synth_design
opt_design
place_design
route_design

# Generate output files
write_bitstream -force ../output/${module_name}/bit/${module_name}.bit
write_hw_platform -fixed -force -file ../output/${module_name}/bit/${module_name}.xsa

close_project