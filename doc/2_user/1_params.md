### *ApexHDL Documentation*
# 2.1. Parameters

## 2.1.1. Console

### 2.1.1.1. Tool call

- ApexHDL is a command-line tool, without user interface.
- To call the tool, **you must be in `src/` sub-folder and run the following command:**
```bash
python apexhdl.py <args>
```

### 2.1.1.2. Parameters specification

- Replace `<args>` with a series of `--flag val`, where `flag` is the name of the parameter, and `val` the value you want to assign to it.
- On the console, parameters name are **in `kebab-case`** (e.g. `method_name` would be `--method-name` on the console).

## 2.1.2. Parameters list

### 2.1.2.1. Quick notes

- In the tables below, `Necessity` column details when you **must specify a value** to the parameter.
- `Benchmark` column tells whether or not this parameter **can be assigned to multiple values**, used in benchmarking mode (detailed in **2.2.**).

### 2.1.2.2. Meta-parameters
| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `help` | - | Flag for printing console user manual | - | - |
| `config` | `str` | Path of a JSON file containing configuration (see **2.1.3.**) | - | - |

### 2.1.2.3. General
| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `method_name` | Value in `{"rom", "unary", "hybrid", "bipartite", "symmetric"}` | Name of the circuit generation method:<br>- `rom`: single ROM,<br>- `unary`: purely unary,<br>- `hybrid`: hybrid binary/unary,<br>- `bipartite`: bipartite,<br>- `symmetric`: symmetric bipartite | Always | **Yes** |
| `circuit_name` | `str` | Name of the generated circuit | Always | No |
| `output_folder` | `str` | Path of the folder which will contain all generated artifacts | Always | No |
| `step` | Value in `{"sim", "syn", "syn-pnr", "impl", "all"}` | Executed stages besides generation and simulation:<br>- `sim`: nothing more,<br>- `syn`: reporting after synthesis,<br>- `syn-pnr`: reporting after place-and-route,<br>- `impl`: on-chip validation,<br>- `all`: all of them | Always | No |

### 2.1.2.4. Maths

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `math_function` | `str` | Mathematical function to be approximated (see **2.1.4.**) | Always | **Yes** |
| `x_min` | `float` | Minimum X value | Always | No |
| `x_max` | `float` | Maximum X value | Always | No |
| `y_min` | `float` | Minimum Y value | Always | No |
| `y_max` | `float` | Maximum Y value | Always | No |

### 2.1.2.5. Bit-precision

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `data_width` | `int` | Word length of input/output values | Always | **Yes** |
| `segmentid_width` | `int` | Bits indexing segments (for hybrid, bipartite, and symmetric) | When `method_name` in `{"hybrid", "bipartite", "symmetric"}`<br>> Defaults to $\lfloor$ `data_width` $/2\rfloor$ | No |
| `groupid_width` | `int` | Bits indexing group of segments (for bipartite, and symmetric) | When `method_name` in `{"bipartite", "symmetric"}`<br>> Defaults to $\lfloor$ `data_width` $/4\rfloor$ | No |

### 2.1.2.6. Tools

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `sim_tool` | Value in `{"ghdl"}` | Tool used for behavioral simulation:<br>- `ghdl`: GHDL | When `step` is `"sim"` | No |
| `eda_tool` | Value in `{"vivado"}` | Tool used for synthesis, place, and route:<br>- `vivado`: Vivado | When `step` in `{"syn", "syn-pnr", "impl"}` | No |

### 2.1.2.7. Target FPGA

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `fpga_board` | Value in `{"xc7z020clg400-1"}` | Target FPGA part number:<br>- `xc7z020clg400-1`: PYNQ-Z2 | When `step` in `{"syn", "syn-pnr", "impl"}` | No |
| `ip_address` | `str` | Target FPGA IP address | When `step` is `impl` | No |
| `username` | `str` | Target FPGA SSH username | When `step` is `impl` | No |
| `password` | `str` | Target FPGA SSH password | When `step` is `impl` | No |
| `fpga_workdir` | `str` | Target FPGA working directory.<br>**WARNING**: Files will be transferred and executed in this folder | When `step` is `impl` | No |

## 2.1.3. Appendix 1: JSON config file (`config`)

- Except for the meta-parameters (in **2.1.2.2.**), parameters can be **defined in a JSON file** (see examples in the `examples/` sub-folder).
- Following JSON conventions, parameters keys must be **in `snake_case`**, as defined in the parameters list in **2.1.2.**.
- Once the JSON is defined, you can specify it while calling the tool:
```bash
python apexhdl.py --config <path-to-json-file> [ <args> ]
```
- Values read in the JSON are **default values**, and can thus be overriden by the `<args>` coming after.

## 2.1.4. Appendix 2: Mathematical expression parsing (`math_function`)

- Internally, ApexHDL uses SymPy for **mathematical expression parsing** (see documentation [here](https://docs.sympy.org/latest/index.html)).
- Thus, function expressions must be **between double quotes** and strictly **Python-style**.
- For instance, $200 \times \exp(-\frac{(x-128)^2}{2 \times 30^2})$ will be written `200*exp(-(x-128)**2/(2*30**2))` in Python-style.
