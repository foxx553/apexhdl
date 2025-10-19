# FPGA Evaluator

## `constraints`
- `*.xdc` = Contraints file which specifies rules on FPGA implementation

## `notebooks`
- `*.bit` = Bitstream to be implemented on the FPGA
- `*.hwh` = XML file which specifies informations about the hardware to be implemented
- `*.ipynb` = Jupyter notebook to communicate with the implemented design through PYNQ framework

## `scripts`
- `*.py` = Python script to generate VHDL code for the core evaluator modules

## `sources`
- `.vhd` = VHDL code for the core evaluator modules

## `wrappers`
- `.tcl` = TCL script to wrap the core evaluator module into a complete block design involving, among others, the Processing System, AXI GPIOs, ...
- `*.jpg` = Illustration to show what the wrapper does