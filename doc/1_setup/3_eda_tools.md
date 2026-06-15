### *ApexHDL Documentation*
# 1.3. EDA tools

## 1.3.1. List of supported EDA tools & targets

| Tool                  | Editor                | Executable    | Target(s)                     |
| :-------------------- | :-------------------- | :------------ | :---------------------------- |
| Vivado Design Suite   | AMD (formerly Xilinx) | `vivado`      | `xc7z020clg400-1` (PYNQ-Z2)   |

## 1.3.2. Vivado Design Suite

- ApexHDL supports Vivado Design Suite for synthesis.
- Install Vivado, by downloading the installer in the [downloads page](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools.html). **Vivado 2024.1 or later** should work.
- Make sure that Vivado is **added to the PATH environment variable**.
- **Check that `vivado` command is recognized** by typing the following command:
```bash
vivado -version
```

### 1.3.2.1. PYNQ-Z2 specifics
- ApexHDL supports PYNQ-Z2 target (`xc7z020clg400-1`), described in [TUL product specification](https://www.tulembedded.com/fpga/ProductsPYNQ-Z2.html). 
- This board is compatible with the PYNQ framework, documented [here](https://pynq.readthedocs.io/en/latest/). 
- The tool takes advantage of this and uses SSH connection with the board, which is made possible when the PYNQ-Z2 runs PYNQ Linux.
- The following material is needed, besides the PYNQ-Z2:
    1. Micro-USB cable,
    2. Ethernet cable,
    3. Micro-SD card.
- Hereafter, the set-up needed before running on-chip validation via ApexHDL:
    1. Add [PYNQ-Z2 board files](https://dpoauwgwqsy2x.cloudfront.net/Download/pynq-z2.zip) in Vivado, as described in the [documentation](https://pynq.readthedocs.io/en/latest/overlay_design_methodology/board_settings.html#vivado-board-files),
    2. Flash [PYNQ Linux image](https://download.amd.com/opendownload/pynq/pynq_z2_v3.1.1.zip) on a Micro-SD card, like described in the [documentation](https://pynq.readthedocs.io/en/latest/getting_started/other_boards.html#microsd-card-setup), and plug it in the PYNQ-Z2,
    3. Set-up the network connection with the PYNQ-Z2, as described in the [documentation](https://pynq.readthedocs.io/en/latest/getting_started/pynq_z2_setup.html#network-connection), and plug your PYNQ-Z2 to a router or your laptop via Ethernet.
- To be sure that the network set-up is good, open a terminal and start an SSH connection to the PYNQ-Z2:
```bash
ssh xilinx@192.168.2.99 # Default password is "xilinx"
```
