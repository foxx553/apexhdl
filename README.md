# ApexHDL

## Credits
- Developer/maintainer: **Florian DELHON**
- Authors: **Florian DELHON, Kevin PEYMANI, Tarek OULD-BACHIR**

## Features
**Automated toolchain** for quick **prototyping**, **validation** and **benchmarking** of **unary and binary hardware function evaluators**. Handles everything for the user, **from the VHDL module generation to the on-chip validation**.

- **Generation** of synthesizable VHDL **module for function evaluation**, using **unary and binary techniques**.
- **Generation** of VHDL exhaustive **testbench**.
- **GHDL** simulation and **Python** plotting for **module validation**.
- **Vivado** synthesis/implementation for complete **hardware reporting (timing, resources, power)**.
- Wrapping in **AXI-stream design** for **on-chip validation** (**PYNQ framework** supported).
- **Benchmarking** feature for **design exploration** (generation techniques, bits of precision, ...) with **results compiled in a CSV file**.
