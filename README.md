<h1 style="text-align: center;">ApexHDL</h1>

**Automated toolchain** for quick **prototyping**, **validation** and **benchmarking** of **hardware function evaluators**. Handles everything for the user, **from the VHDL module generation to the on-chip validation**.

- **Generation** of synthesizable VHDL **module for function evaluation**, using **unary and binary techniques**.
- **Behavioral simulation** and **Python** plotting for **module validation**.
- Standalone synthesis for hardware reporting of **timing and resources metrics**.
- **Hardware-In-the-Loop** process for module **validation on physical silicon**. 
- **Benchmarking** feature for **design exploration** (generation techniques, bits of precision, ...) with **results compiled in a CSV report**.


## Repository
- `doc/` = **Complete documentation** for ApexHDL set-up, usage, and codebase.
- `src/` =
    - `apexhdl.py` = **Main Python script**, to be called in order to use ApexHDL.
    - `apex/` = Python source code.
- `tcl/` = Tcl scripts, used for **hardware reporting** and **on-chip validation**.
- `xdc/` = XDC constraints scripts, used for **hardware reporting** and **on-chip validation**.

## Highlights

### 1. Type one command, that's it!

```json
{
    "method_name": "bipartite",
    "circuit_name": "apex_test",
    "output_folder": "../output",
    "step": "all",
    "math_function": "4*((1.35*x-1)**3+(1.35*x-1)**2)+0.2", 
    "x_min": 0,
    "x_max": 1,
    "y_min": 0,
    "y_max": 1,
    "data_width": 8,
    (...)
}
```

```bash
python apexhdl.py --config apex_test.json
```

### 2. ApexHDL generates your VHDL evaluator...

```vhdl
entity apex_test is
    port (
        input_a     : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result      : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end apex_test;

architecture arch_apex_test of apex_test is
    (...)
end arch_apex_test;
```

### 3. ... runs behavioral simulation

<img src="doc/img/sim_curves.svg" width="31.5%" /> <img src="doc/img/sim_abs_err.svg" width="32%" /> <img src="doc/img/sim_rel_err.svg" width="32%" />

### 4. ... retrieves hardware metrics

```
Timing Report
    Data Path Delay:        8.931ns
(...)
```

```
|      Instance     | Module | Total LUTs |
+-------------------+--------+------------+
| top_apex_test     |  (top) |         15 |
(...)
```

### 5. ... tests it on physical silicon

<img src="doc/img/impl_curves.svg" width="31.5%" /> <img src="doc/img/impl_abs_err.svg" width="32%" /> <img src="doc/img/impl_rel_err.svg" width="32%" />

### 6. ... and leaves you with a complete report

```
Results
----------------------
SimMaxAbsError: 0.08621918465850054
SimMeanAbsError: 0.014783697695412
SimMaxRelError: 0.40624999999999994
SimMeanRelError: 0.03827368451958165
LutCount: 15
CriticalPathLatency (ns): 8.931
ImplMaxAbsError: 0.08621918465850054
ImplMeanAbsError: 0.014783697695412
ImplMaxRelError: 0.40624999999999994
ImplMeanRelError: 0.03827368451958165
```

## Benchmarking mode

### 1. Define multiple values for one parameter

```json
{
    "method_name": ["rom", "unary", "hybrid", "bipartite", "symmetric"],
    (...)
}
```

### 2. ApexHDL runs all possible combinations...

```bash
apexhdl - INFO - Starting ApexHDL...
apex.runner - INFO - Running config 1 of 5...
(...)
apex.runner - INFO - Running config 2 of 5...
(...)
apex.runner - INFO - Running config 3 of 5...
(...)
apex.runner - INFO - Running config 4 of 5...
(...)
apex.runner - INFO - Running config 5 of 5...
(...)
```

### 3. ... and leaves you with a complete CSV report

| MethodName  | SimMaxAbsError | SimMeanAbsError | SimMaxRelError | SimMeanRelError | LutCount | CriticalPathLatency (ns) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| rom | 0.016 | 0.002 | 0.057 | 0.005 | 31 | 7.91 |
| unary | 0.016 | 0.002 | 0.057 | 0.005 | 32 | 7.99 |
| hybrid | 0.016 | 0.002 | 0.057 | 0.005 | 46 | 10.31 |
| bipartite | 0.086 | 0.015 | 0.406 | 0.038 | 15 | 8.93 |
| symmetric | 0.081 | 0.015 | 0.406 | 0.040 | 27 | 9.41 |

## Citation
- Authors: **Florian DELHON**, **Kevin PEYMANI**, **Tarek OULD-BACHIR**.
- Paper Title: **ApexHDL: A Tool for Generating/Benchmarking Unary and Binary Function Evaluators on FPGA**.

## Contact
- Developer/maintainer: **Florian DELHON**, florian.delhon@polymtl.ca. *Feel free to contact me if you'd like to know more about the tool and eventually contribute to its development!*
