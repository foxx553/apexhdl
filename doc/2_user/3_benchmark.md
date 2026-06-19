### *ApexHDL Documentation*
# 2.3. Benchmark

## 2.3.1. Configuration

- From the moment you define **multiple values for a parameter**, ApexHDL automatically **runs all possible combinations**.
- If we take the exemple of the `data_width` parameter, it would take that form on the console:
```bash
--data-width 8 10 12 
```
- ... while it would use a JSON array instead in the context of a JSON configuration:
```bash
"data_width": [8, 10, 12],
```
- **/!\\ Disclaimer:** To prevent unforeseen tool behavior, this benchmarking mode is only enabled for a few parameters (see parameters list in **2.1.2.**). It may evolve in the future.

## 2.3.2. Outputs

### 2.3.2.1. Folder structure

- In the context of a benchmark, the `circuit_name` parameter takes the role of the benchmark's name.
- All benchmarking outputs are placed in folder `output_folder/<circuit_name>/`.
- Each combination takes the name `<circuit_name><id>`, where `<id>` is a unique ID.
- Each `<circuit_name><id>` results in a folder `output_folder/<circuit_name>/<circuit_name><id>/`, in which all outputs described in **2.2.** are placed for that particular circuit.

### 2.3.2.2. Final report

- The results of all combinations are placed in a CSV report `output_folder/<circuit_name>/<circuit_name>.csv`.
- Each line of the CSV represents a combination `<circuit_name><id>`, a contains the most relevant parameters and all retrieved metrics.
- The CSV report can then be opened and/or processed the way you want to perform your own comparative analysis.
