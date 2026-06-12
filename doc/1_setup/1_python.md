### *ApexHDL Documentation*
# 1.1. Python environment

## 1.1.1. Python version check

- ApexHDL needs Python installed on the host computer.
- Any **version above Python 3.10** should work.
- Check if Python is installed with the following command:
```bash
python --version
```
- If the command is not recognized or Python is too old, please refer to **1.1.2**.
- If everything's fine, jump to **1.1.3**.

## 1.1.2. Python installation

- To install Python, please refer to Python [official documentation](https://docs.python.org/3/using/index.html) and [downloads page](https://www.python.org/downloads/).
- Make sure that Python is **added to the PATH environment variable**.
- Run version check detailed in **1.1.1.** to be sure that Python is installed and known.

## 1.1.3. Virtual environment

- To isolate ApexHDL's dependencies, you should set-up a virtual environment.
- In the `apexhdl` root folder, create the virtual environment:
```bash
python -m venv .venv
```
- Activate the environment, it will be necessary every time you open the terminal:
```bash
# in Windows (PowerShell)
.venv\Scripts\Activate.ps1

# in Linux
source .venv/bin/activate
```
- Inside that virtual environment, you can now safely install ApexHDL's dependencies, as detailed in **1.1.4**.

## 1.1.4. Dependencies installation

- ApexHDL's dependencies are listed in `src/requirements.txt`.
- Install these dependencies:
```bash
pip install -r src/requirements.txt
```
- Once installation is complete, you may perform the final detailed in **1.1.5**.

## 1.1.5. Final check

- To validate Python is installed and all dependencies are known, **run the ApexHDL `help` command**:
```bash
python src/apexhdl.py --help
```
