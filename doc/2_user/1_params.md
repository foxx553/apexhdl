### *ApexHDL Documentation*
# 2.1. Parameters

## 2.1.1. Console

- ApexHDL is a command-line tool, without user interface.
- To call the tool, **you must be in `src/` sub-folder and run the following command:**
```bash
python apexhdl.py <args> # Replace <args> with the parameters detailed below
```

## 2.1.2. Parameters list

### 2.1.2.1. Meta-parameters
| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `help` | - | Flag for printing console user manual | - | - |
| `config` | `str` | Path of a JSON file containing configuration | - | - |

### 2.1.2.2. General
| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `method_name` | Value in `{"rom", "unary", "hybrid", "bipartite", "symmetric"}` | Name of the circuit generation method:<br>- `rom`: single ROM,<br>- `unary`: purely unary,<br>- `hybrid`: hybrid binary/unary,<br>- `bipartite`: bipartite,<br>- `symmetric`: symmetric bipartite | Always | **Yes** |
| `circuit_name` | `str` | Name of the generated circuit | Always | No |
| `output_folder` | `str` | Path of the folder which will contain all generated artifacts | Always | No |
| `step` | Value in `{"sim", "syn", "syn-pnr", "impl"}` | Executed stages:<br>- `sim`: simulation,<br>- `syn`: reporting after synthesis,<br>- `syn-pnr`: reporting after place-and-route,<br>- `impl`: on-chip validation | Always | No |

### 2.1.2.3. Maths

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `math_function` | `str` | Mathematical function to be approximated | Always | **Yes** |
| `x_min` | `float` | Minimum X value | Always | No |
| `x_max` | `float` | Maximum X value | Always | No |
| `y_min` | `float` | Minimum Y value | Always | No |
| `y_max` | `float` | Maximum Y value | Always | No |

### 2.1.2.4. Bit-precision

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `data_width` | `int` | Word length of input/output values | Always | **Yes** |
| `segmentid_width` | `int` | Bits indexing segments (for hybrid, bipartite, and symmetric) | When `method_name` in `{"hybrid", "bipartite", "symmetric"}`<br>> Defaults to $\lfloor$`data_width`$/2\rfloor$ | No |
| `groupid_width` | `int` | Bits indexing group of segments (for bipartite, and symmetric) | When `method_name` in `{"bipartite", "symmetric"}`<br>> Defaults to $\lfloor$`data_width`$/4\rfloor$ | No |

### 2.1.2.5. Tools

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `sim_tool` | Value in `{"ghdl"}` | Tool used for behavioral simulation:<br>- `ghdl`: GHDL | When `step` is `"sim"` | No |
| `eda_tool` | Value in `{"vivado"}` | Tool used for synthesis, place, and route:<br>- `vivado`: Vivado | When `step` in `{"syn", "syn-pnr", "impl"}` | No |

### 2.1.2.6. Target FPGA

| Name | Type | Description | Necessity | Benchmark |
| --- | --- | --- | --- | --- |
| `fpga_board` | Value in `{"xc7z020clg400-1"}` | Target FPGA part number:<br>- `xc7z020clg400-1`: PYNQ-Z2 | When `step` in `{"syn", "syn-pnr", "impl"}` | No |
| `ip_address` | `str` | Target FPGA IP address | When `step` is `impl` | No |
| `username` | `str` | Target FPGA SSH username | When `step` is `impl` | No |
| `password` | `str` | Target FPGA SSH password | When `step` is `impl` | No |
| `fpga_workdir` | `str` | Target FPGA working directory.<br>**WARNING**: Files will be transferred and executed in this folder | When `step` is `impl` | No |

## 2.1.3. Appendix 1: JSON config file (`--config`)

## 2.1.4. Appendix 2: Mathematical expression parsing (`--math-function`)

## 2.1.5. Appendix 3: Examples
