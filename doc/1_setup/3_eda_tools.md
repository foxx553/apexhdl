### *ApexHDL Documentation*
# 3.2. EDA tools

## 3.2.1. List of supported EDA tools & targets

| Tool                  | Editor                | Executable    | Target(s)                     |
| :-------------------- | :-------------------- | :------------ | :---------------------------- |
| Vivado Design Suite   | AMD (formerly Xilinx) | `vivado`      | `xc7z020clg400-1` (PYNQ-Z2)   |

## 3.2.2. Vivado Design Suite

- ApexHDL supports Vivado Design Suite for synthesis.
- Install Vivado, by downloading the installer in the [downloads page](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools.html). **Vivado 2024.1 or later** should work.
- Make sure that Vivado is **added to the PATH environment variable**.
- **Check that `vivado` command is recognized** by typing it in command line.

**>>> Target support: `xc7z020clg400-1`**
- ApexHDL supports PYNQ-Z2 target (`xc7z020clg400-1`), described in [TUL product specification](https://www.tulembedded.com/fpga/ProductsPYNQ-Z2.html).
- Add [PYNQ-Z2 board files](https://dpoauwgwqsy2x.cloudfront.net/Download/pynq-z2.zip) in Vivado, so that it knows the boards' physical features.
