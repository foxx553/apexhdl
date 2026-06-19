### *ApexHDL Documentation*
# 3.1. Codebase structure

## 3.1.1. Pipeline parametrization (`apex.Context`)

### 3.1.1.1. Structure

- `Context` is the core class containing **all parameters** ApexHDL handles.
- It is a `dataclass`, thus not containing any method besides its long list of attributes.
- For each field, the following pattern is applied:
```python
    parameter_name: <param-type> = field(metadata={
        "description": "<param-description>",
        "group": "<param-group>",
        "allow_multiple": <param-multiple-bool>
    })
    """<param-description>"""
```
- It motivated by the following reasons:
    - `<param-type>` and `"""<param-description>"""` allows for clean **code documentation**, as described in **3.1.6.**,
    - `metadata` (and also the `<param-type>`) are used to dynamically **build the parser** at startup, as described in **3.1.2.** 

### 3.1.1.2. Roles

- As documented in the following sections, the `Context` is used throughout ApexHDL execution:
    - At startup, a **parser is built** tailored to the `Context` fields (see **3.1.2.**),
    - User args are parsed, and values are **encapsulated in an instance of `Context`**,
    - Stage registries use it to **select the appropriate variant** (see **3.1.3.**),
    - It is used by each variant to **parameterize** their algorithm.

## 3.1.2. Pipeline initialization/execution (`apex.{Runner, Pipeline}`)

### 3.1.2.1. Initialization

- `Runner` is the **first class called** at runtime.
- It contains methods for **initializing ApexHDL execution**, namely:
    - Building an **arguments parser** adapted to `Context` fields,
    - **Parsing** user arguments against this newly created parser,
    - Dealing with **JSON parsing** when parameters are defined in JSON file,
    - Dealing with **benchmarking mode **when there are several combinations specified by the user.
- For each circuit, it:
    - Populates a `Context` instance,
    - Starts ApexHDL pipeline execution by building a `Pipeline` instance (see **3.1.2.2.**).

### 3.1.2.2. Execution

- `Pipeline` is the orchestrator for **one pipeline execution**.
- In its constructor, it uses a `Context` instance to **select the variants** of each step of the pipeline (see **3.1.3.**).
- When prompted to, it runs each step one after the other, and **returns all outputs retrieved** throughout the pipeline (see **3.1.4.**).

## 3.1.3. Variants registration/selection

### 3.1.3.1. `Registry` definition

- A "registry" design pattern is used to **register and select variants** within a pipeline stage.
- In each `apex.*_stage.*Registry`, there are two classes defined:
    - A `*Stage` class which is the **base class** for all variants of the stage, defining the abstract `execute` method,
    - A `*Registry` class which is the **registering class**, importing all variants and selecting the appropriate one based on the `Context` instance passed.

### 3.1.3.2. Variants predicates

- Each variant consists in a class in `apex.*_stage.variants` package.
- Each variant class is meant to be **"self-contained"**, in the sense that all its informations should be in its Python file.
- It thus includes variant selection criteria, which takes the form of a **decorator placed above** class declaration.
- Here's the example of the bipartite generation variant:
```python
@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "bipartite", priority=1)
class GenerationBipartite(GenerationStage):
    (...)
```
- In this example:
    - `predicate` is the **condition checker**, returning a boolean, which selects this variants if `True` (here, when `method_name` is `"bipartite"`),
    - `priority` lets you **order condition checking** among the variants of a stage (higher priorities are evaluated first).
- This registry is ultimately used by the `Pipeline` to retrieve its appropriate variant (see **3.1.2.2.**).

## 3.1.5. Tcl/XDC files

- To perform hardware-related operations in EDA tools, the codebase includes **Tcl and XDC scripts**.
- At the moment, ApexHDL works with Vivado for the Zynq-7020 FPGA target, and thus contains the following scripts:
    - `tcl/analyze_evaluator.tcl`, associated with `xdc/virtual_clk.xdc`, for hardware reporting (see **3.2.4.**),
    - `tcl/{implement_evaluator.tcl, wrap_evaluator.tcl}`, associated with `xdc/pynq_z2.tcl`, for on-chip validation (see **3.2.5.**).

## 3.1.6. Documentation, linting & logging

### 3.1.6.1. Code documentation

- The code is intentionnally **documented in depth**, since it is intended to be extended by anyone.
- Thus:
    - Every **variable type** is explicitly written,
    - Each **class attribute is commented** so that hovering it lets us understand its purpose,
    - Each **method is commented** (notably its purpose, parameters, and return values) so that hovering it lets us understand its use.
- Concretely, ApexHDL was developed in VSCode using **Python strict type checking**:
    - To activate it, go in settings and change parameter `python.analysis.typeCheckingMode` to `strict`.
  
### 3.1.6.2. Logging

- ApexHDL codebase uses Python default `logging` package (documented [here](https://docs.python.org/3/library/logging.html)) in order to provide to the user logging of the different execution steps.
- Logging messages take the following form:
```bash
<date-and-time> - <class-name> - <log-level> - <message>
```
- To perpetuate variants' self-containment, they have **ready-to-use logger object** (called with `self.logger`), previously defined in `*Registry` class.
