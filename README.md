# ApexHDL

## Credits
- Authors: **Florian DELHON, Kevin PEYMANI, Tarek OULD-BACHIR**
- Main developer/maintainer: **Florian DELHON**

## Features
**Automated toolchain** for quick **prototyping**, **validation** and **benchmarking** of **unary and binary hardware function evaluators**. Handles everything for the user, **from the VHDL module generation to the on-chip validation**.

- **Generation** of synthesizable VHDL **module for function evaluation**, using **unary and binary techniques**.
- **Generation** of VHDL exhaustive **testbench**.
- **GHDL** simulation and **Python** plotting for **module validation**.
- **Vivado** synthesis/implementation for complete **hardware reporting (timing, resources, power)**.
- Wrapping in **AXI-stream design** for **on-chip validation** (**PYNQ framework** supported).
- **Benchmarking** feature for **design exploration** (generation techniques, bits of precision, ...) with **results compiled in a CSV file**.

## Table of contents
1. [Getting started](#getting-started)
2. [User guide](#user-guide)
3. [Developer guide](#developer-guide)

## Getting started

### Prerequisite: GHDL
ApexHDL currently supports GHDL for module simulation, as it is a lightweight open-source VHDL simulator, supported on Linux, Windows and macOS. All necessary informations can be found on its [GitHub page](https://github.com/ghdl/ghdl).

- Install GHDL on your computer.
- Add it to your `PATH` so that the `ghdl` command is known to your console.

### Prerequisite: Vivado
ApexHDL currently supports PYNQ-Z2 board (see [TUL product specification](https://www.tulembedded.com/fpga/ProductsPYNQ-Z2.html)). Thus, it uses the official Vivado software for both designing, synthesizing and implementing (see [Vivado official documentation](https://docs.amd.com/r/en-US/ug896-vivado-ip/Vivado-Design-Suite-Documentation)).

- Install Vivado Design Suite (see [Vivado downloads page](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools.html)), version 2024.1 or later should be working.
- Add it to your `PATH` so that the `vivado` command is known to your console.

### Python setup
ApexHDL is written in Python. Source code is in `./src` folder.

- If necessary, install Python (see [Python downloads page](https://www.python.org/downloads/)) and add it to your `PATH` so that the `python` command is known to your console.
- Go into `./src` folder.
- **[Recommended]** Create a virtual environment and activate it to prevent any conflicts with other projects (see [Python `venv` official documentation](https://docs.python.org/3/library/venv.html)). Don't forget to activate it every single time you open the console.
- Install dependencies by running the following command.
```bash
pip install -r requirements.txt 
```

## User guide

### General
ApexHDL allows you to run the automated toolchain to generate and validate hardware function evaluator with just one command.

#### Help
For help, the following command will show you all customization options.
```bash
python ./apex_hdl.py --help
```

#### JSON config file (`--config`)
Since it is not handy to specify all options in one long command, you may use the `--config` flag to specify a JSON file which will contain all your options. The `config.json` file is an example of a complete JSON file. Here's an example usage.
```bash
python ./apex_hdl.py --config ./config.json
```

- Note 1: All keys in the JSON file use `_` as separators, instead of `-`. For instance, `--method-name` CLI flag corresponds to `method_name` key in the JSON file.
- Note 2: Values specified in the JSON file are default values. Thus, subsequent CLI args can be specified, and will override JSON values.

#### Mathematical expression parsing (`--math-function`)
Internally, ApexHDL uses SymPy for mathematical expression parsing (see [SymPy official documentation](https://docs.sympy.org/latest/index.html)).

- Note 1: ApexHDL currently supports only single-variable functions of $x$.
- Note 2: SymPy has its own conventions for mathematical expressions. For instance, $200 \times \exp(-\frac{(x-128)^2}{2 \times 30^2})$ will be written `200*exp(-(x-128)**2/(2*30**2))` for SymPy parsing.

### Normal vs. Benchmarking mode
ApexHDL offers an easy-to-use benchmarking mode. All you need is to specify an array of values for one (or more) option(s). When ApexHDL detects this, it will compute all possible combinations, launch the whole toolchain for each combination, and finally gather all data into a single CSV file to let you compare these different combinations. The `bench.json` file is an example of a JSON file specifying a benchmark.

- Note 1: That benchmarking mode is supported for options `method_name`, `math_function` and `data_width`.
- Note 2: Resulting file will be produced as follows. In the `output_folder`, each combination will be named `<circuit_name><ID>` (e.g. `eval005`), and a file `<circuit_name>.csv` (e.g. `eval.csv`) will contain all data.
- Note 3: In JSON file, you'll specify an array of values as follows (example of `data_width`).
```json
"data_width": [8, 10, 12]
```
- Note 4: In CLI, you'll specify an array of values as follows (same example).
```bash
--data-width 8 10 12
```

## Developer guide

### Overview
ApexHDL pipeline is fundamentally built around the following four steps: generation, simulation, analysis and implementation.

#### Generation step (`apex.generation_stage.*`)
Consists in generating the VHDL circuit for hardware function evaluation.

#### Simulation step (`apex.simulation_stage.*`)
Consists in generating the VHDL exhaustive testbench for the generated circuit, running the simulation using GHDL, and plotting with Python the results and how our circuit compares to the theoretical mathematical function.

#### Analysis step (`apex.analysis_stage.*`)
Consists in running Vivado synthesis and implementation of the circuit alone, and saving hardware reports (timing, resources, power) produced by Vivado.

#### Implementation step (`apex.implementation_stage.*`)
Consists in wrapping the circuit into a complete block design allowing AXI-stream communication, generating the bitstream, and process to a hardware-in-the-loop process programming the target and running the evaluator on physical silicon.

### Pipeline initialization/execution (`apex.{initializer, pipeline}`)
The `Initializer` class contains the parser used to get all args passed by the user and to start execution (managed by the `Pipeline` class). Note that the parser must be compatible with the definition of the `Context` class (see the next paragraph). To allow the definition of multiple values (for the benchmark mode), the following option must be specified when adding the argument to the parser.
```python
nargs="+"
```

### Pipeline parametrization (`apex.context`)
`Context` is the core data class containing all arguments passed by the user. It is used throughout the pipeline execution for the following uses.
- Selection of the correct variant for each step, thanks to the "Registry" design pattern (see next paragraph).
- Parametrization of the chosen algorithms in order to produce the correct outputs, thanks to the `ctx` arg in the `execute()` method of each variant.

### Variants selection (`apex.*_stage.variants.*`)

The "Registry" design pattern is used to register all possible variants, and then select the correct ones (done in the constructor of `Pipeline`). As mentioned above, the `Context` instance contains all necessary informations for the selection. Thus, for each variant, a decorator is defined to specify the conditions that have to be met to select it. For instance, the variant `GenerationHybrid` is called for the generation step if the `method_name` is `hybrid`, as shown below. With the priority mechanism (checking first higher priorities), there's a lot of flexibility for variants selection.

```python
@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "hybrid", priority=1)
class GenerationHybrid(GenerationStage):
    (...)
```

