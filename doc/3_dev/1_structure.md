### *ApexHDL Documentation*
# 3.1. Codebase structure

## 3.1.1. Pipeline parametrization (`apex.Context`)

### 3.1.1.1. Structure

- `Context` is the core class containing all existing parameters ApexHDL handles.
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
    - `<param-type>` and `"""<param-description>"""` allows for great code documentation, as described in **3.1.6.**,
    - `metadata` (and also the `<param-type>`) are used to dynamically build the parser at startup, as described in **3.1.2.** 

### 3.1.1.2. Roles

- As documented in the following sections, the `Context` is used throughout ApexHDL execution:
    - At startup, a parser is built tailored to the `Context` fields (see **3.1.2.**),
    - User args are parsed, and values are encapsulated in an instance of `Context`,
    - Stage registries use it to select the appropriate variant (see **3.1.3.**),
    - It is used by each variant to parameterize their algorithm.

## 3.1.2. Pipeline initialization/execution (`apex.{Runner, Pipeline}`)

### 3.1.2.1. Initialization

- `Runner` is the first class called at runtime.
- It contains methods for initializing ApexHDL execution, namely:
    - Building an arguments parser adapted to `Context` fields,
    - Parsing user arguments against this newly created parser,
    - Dealing with JSON parsing when parameters are defined in JSON file,
    - Dealing with benchmarking mode when there are several combinations specified by the user.
- For each circuit, it:
    - Populates a `Context` instance,
    - Starts ApexHDL pipeline execution by building a `Pipeline` instance (see **3.1.2.2.**).

### 3.1.2.2. Execution

- `Pipeline` is the orchestrator for **one pipeline execution**.
- In its constructor, it uses a `Context` instance to select the variants of each step of the pipeline (see **3.1.3.**).
- When prompted to, it runs each step one after the other, and returns all outputs retrieved throughout the pipeline (see **3.1.4.**).

## 3.1.3. Variants registration/selection

### 3.1.3.1. `Registry` definition

- A "registry" design pattern is used to register and select variants within a pipeline stage.
- In each `apex.*_stage.*Registry`, there are two classes defined:
    - A `*Stage` class which is the base class for all variants of the stage, defining the abstract `execute` method,
    - A `*Registry` class which is the registering class, importing all variants and selecting the appropriate one based on the `Context` instance passed.

### 3.1.3.2. Variants predicates

- Each variant consists in a class in `apex.*_stage.variants` package.
- Each variant class is meant to be "self-contained", in the sense that all its informations should be in its Python file.
- It thus includes variant selection criteria, which takes the form of a decorator placed above class declaration.
- Here's the example of the bipartite generation variant:
```python
@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "bipartite", priority=1)
class GenerationBipartite(GenerationStage):
    (...)
```
- In this example:
    - `predicate` is the condition checker, returning a boolean, which selects this variants if `True` (here, when `method_name` is `"bipartite"`),
    - `priority` lets you order condition checking among the variants of a stage (higher priorities are evaluated first).
- This registry is ultimately used by the `Pipeline` to retrieve its appropriate variant (see **3.1.2.2.**).

## 3.1.5. TCL/XDC files

## 3.1.6. Documentation, linting & logging
