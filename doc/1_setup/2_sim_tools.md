### *ApexHDL Documentation*
# 1.2. Simulation tools

## 1.2.1. List of supported simulation tools

| Tool                  | Editor                | Executable    |
| :-------------------- | :-------------------- | :------------ |
| GHDL                  | *open-source*         | `ghdl`        |

## 1.2.2. GHDL

- ApexHDL supports GHDL for the RTL simulation of the generated VHDL files.
- Install GHDL, with all informations on its [GitHub page](https://github.com/ghdl/ghdl).
- Make sure that GHDL is **added to the PATH environment variable**.
- **Check that `ghdl` command is recognized** by typing the following command:
```bash
ghdl --version
```