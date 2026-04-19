# Get command line arguments
set output_folder [lindex $argv 0]
set module_name [lindex $argv 1]

# Create in-memory project
create_project -in_memory -part xc7z020clg400-1

# Add VHDL source and constraints files
add_files ${output_folder}/${module_name}/vhdl/${module_name}.vhd
add_files ${output_folder}/${module_name}/vhdl/stream_top_${module_name}.vhd
add_files ../xdc/pynq_z2.xdc

# Set-up VHDL-2008 for evaluator module
set_property FILE_TYPE {VHDL 2008} [get_files ${output_folder}/${module_name}/vhdl/${module_name}.vhd]

# Set top module and update compilation order
set_property TOP stream_top_${module_name} [current_fileset]
set_property source_mgmt_mode All [current_project]
update_compile_order -fileset sources_1

# Create block design using custom wrapper script
source ../tcl/wrap_evaluator.tcl
update_compile_order -fileset sources_1
create_root_design "" stream_top_${module_name}
save_bd_design
validate_bd_design

# Generate all targets from block design
set bd_file [get_files *.bd]
generate_target all $bd_file

# Create and add wrapper for the block design
make_wrapper -files [get_files $bd_file] -top
add_files -norecurse ../src/.gen/sources_1/bd/evaluator/hdl/evaluator_wrapper.v
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
write_bitstream -force ../output/${module_name}/impl/${module_name}.bit
write_hw_platform -fixed -force -file ../output/${module_name}/impl/${module_name}.xsa

# Close project
close_project