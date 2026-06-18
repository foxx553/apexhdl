<h1 style="text-align: center;">ApexHDL</h1>

**Automated toolchain** for quick **prototyping**, **validation** and **benchmarking** of **hardware function evaluators**. Handles everything for the user, **from the VHDL module generation to the on-chip validation**.

- **Generation** of synthesizable VHDL **module for function evaluation**, using **unary and binary techniques**.
- **Behavioral simulation** and **Python** plotting for **module validation**.
- Standalone synthesis for hardware reporting of **timing and resources metrics**.
- **Hardware-In-the-Loop** process for module **validation on physical silicon**. 
- **Benchmarking** feature for **design exploration** (generation techniques, bits of precision, ...) with **results compiled in a CSV report**.

## Highlights

### Normal mode

#### 1. Type one command, that's it!

#### 2. ApexHDL generates your VHDL evaluator...

#### 3. ... runs behavioral simulation

#### 4. ... retrieves hardware metrics

#### 5. ... tests it on physical silicon

#### 6. ... and leaves you with a complete report

### Benchmarking mode

#### 1. Define multiple values for one parameter, that's it!

#### 2. ApexHDL runs all possible combinations...

#### 3. ... and leaves you with a complete CSV report

## Repository
- `doc/` = **Complete documentation** for ApexHDL set-up, usage, and codebase.
- `src/` =
    - `apexhdl.py` = **Main Python script**, to be called in order to use ApexHDL.
    - `apex/` = Python source code.
- `tcl/` = Tcl scripts, used for **hardware reporting** and **on-chip validation**.
- `xdc/` = XDC constraints scripts, used for **hardware reporting** and **on-chip validation**.

## Citation
- Authors: **Florian DELHON**, **Kevin PEYMANI**, **Tarek OULD-BACHIR**.
- Paper Title: **ApexHDL: A Tool for Generating/Benchmarking Unary and Binary Function Evaluators on FPGA**.

## Contact
- Developer/maintainer: **Florian DELHON**, florian.delhon@polymtl.ca. *Feel free to contact me if you'd like to know more about the tool and eventually contribute to its development!*
