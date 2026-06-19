### *ApexHDL Documentation*
# 3.2. Pipeline stages

## 3.2.1. Default variants

- Each stage contains a `default` implementation which:
    - Has a `0` priority,
    - Does nothing.
- It helps keeping higher-level code more systematic (especially `apex.Pipeline`) since, when the user does not want to execute one particular stage, it still goes that same "registry" and escapes through that `default` variant.

## 3.2.2. Generation (`apex.generation_stage.variants.*`)

- This package contains generation variants, i.e.:
    - `generation_bipartite` = Used for bipartite method,
    - `generation_hybrid` = Used for hybrid/binary/unary method,
    - `generation_rom` = Used for single ROM method,
    - `generation_symmetric` = Used for symmetric bipartite method,
    - `generation_unary` = Used for purely unary method.
- The definition of each variant mostly follows methodologies published in the litterature.

## 3.2.3. Simulation (`apex.simulation_stage.variants.*`)

- This package contains simulation variants, i.e.:
    - `simulation_ghdl` = Used to run simulation through GHDL.
- It generates VHDL exhaustive testbench, runs it, and computes mean and max, absolute and relative, errors.
- These errors are returned at the end of the `execute` function (see **3.2.6.**).

## 3.2.4. Hardware reporting (`apex.synthesis_stage.variants.*`)

- This package contains hardware reporting variants, i.e.:
    - `synthesis_vivado` = Uses Vivado to run standalone synthesis of the evaluator.
- It encapsulates the evaluator into a standalone *top-level*, runs synthesis (and eventually place-and-route) before retrieving LUT utilization (and eventually critical path latency).
- These metrics are returned at the end of the `execute` function (see **3.2.6.**).

## 3.2.5. On-chip validation (`apex.implementation_stage.variants.*`)

- This package contains on-chip validation variants, i.e.:
    - `implementation_pynq` = Uses Vivado and PYNQ framework to perform hardware-in-the-loop validation.
- Taking advantage of the PYNQ framework, it runs Vivado bitstream generation of the evaluator encapsulated in AXI-Stream interface, before sending a Python script through SCP.
- This remote script programs the FPGA fabric, stimulates the design, and sends results bach to the computer.
- Results are parsed to compute same errors than during simulation.
- These errors are returned at the end of the `execute` function (see **3.2.6.**).

## 3.2.6. Outputs management

- The `Context` is currently "read-only" after the initial fill by the `apex.Runner`, and is not meant to contain pipeline outputs.
- To manage outputs, the `execute` used for each pipeline stage does return a `dict[str, Any]`.
- Thus, to return the metrics it extracted during its process, each variant returns a dictionary with the metric name as the key, associated with its value.
- The dictionaries returned through all pipeline stages are concatenated together in `apex.Pipeline`, and finally used by the `apex.Runner` to write it in the comprehensive `apex_report.rpt`.
