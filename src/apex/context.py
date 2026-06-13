from dataclasses import dataclass, field
from typing import Optional, Literal 
from pathlib import Path

@dataclass
class Context:
    """
    Context of the ApexHDL execution
    """
    
    # General
    method_name: Literal["rom", "unary", "hybrid", "bipartite", "symmetric"] = field(metadata={
        "description": "Name of the circuit generation method(s): rom = single ROM, unary = purely unary, hybrid = hybrid binary/unary, bipartite = bipartite, symmetric = symmetric bipartite",
        "group": "General",
        "allow_multiple": True
    })
    """Name of the circuit generation method(s): rom = single ROM, unary = purely unary, hybrid = hybrid binary/unary, bipartite = bipartite, symmetric = symmetric bipartite"""

    circuit_name: str = field(metadata={
        "description": "Name of the generated circuit(s)",
        "group": "General"
    })
    """Name of the generated circuit(s)"""

    output_folder: Path = field(metadata={
        "description": "Folder containing all generated artifacts",
        "group": "General"
    })
    """Folder containing all generated artifacts"""

    step: Literal["sim", "syn", "syn-pnr", "impl"] = field(metadata={
        "description": "Executed stages: sim = simulation, syn = reporting after synthesis, syn-pnr = reporting after place-and-route, impl = on-chip validation",
        "group": "General"
    })
    """Executed stages: sim = simulation, syn-synth = reporting after synthesis, syn = reporting after place-and-route, impl = on-chip validation"""

    # Maths
    math_function: str = field(metadata={
        "description": "Mathematical function(s) to be approximated",
        "group": "Maths",
        "allow_multiple": True
    })
    """Mathematical function(s) to be approximated"""

    x_min: float = field(metadata={
        "description": "Minimum X value",
        "group": "Maths"
    })
    """Minimum X value"""

    x_max: float = field(metadata={
        "description": "Maximum X value",
        "group": "Maths"
    })
    """Maximum X value"""

    y_min: float = field(metadata={
        "description": "Minimum Y value",
        "group": "Maths"
    })
    """Minimum Y value"""

    y_max: float = field(metadata={
        "description": "Maximum Y value",
        "group": "Maths"
    })
    """Maximum Y value"""

    # Bit-precision
    data_width: int = field(metadata={
        "description": "Word length(s) of input/output values",
        "group": "Bit-precision",
        "allow_multiple": True
    })
    """Word length(s) of input/output values"""

    segmentid_width: Optional[int] = field(metadata={
        "description": "Bits indexing segments",
        "group": "Bit-precision"
    })
    """Bits indexing segments (for hybrid, bipartite, and symmetric)"""

    groupid_width: Optional[int] = field(metadata={
        "description": "Bits indexing group of segments",
        "group": "Bit-precision"
    })
    """Bits indexing group of segments (for bipartite, and symmetric)"""

    # Tools
    sim_tool: Optional[Literal["ghdl"]] = field(metadata={
        "description": "Tool used for behavorial simulation: ghdl = GHDL",
        "group": "Tools"
    })
    """Tool used for behavorial simulation: ghdl = GHDL"""

    eda_tool: Optional[Literal["vivado"]] = field(metadata={
        "description": "Tool used for synthesis, place, and route: vivado = Vivado",
        "group": "Tools"
    })
    """Tool used for synthesis, place, and route: vivado = Vivado"""
    
    # Target FPGA
    fpga_board: Optional[Literal["xc7z020clg400-1"]] = field(metadata={
        "description": "Target FPGA part number: xc7z020clg400-1 = PYNQ-Z2",
        "group": "Target FPGA"
    })
    """Target FPGA part number: xc7z020clg400-1 = PYNQ-Z2"""

    ip_address: Optional[str] = field(metadata={
        "description": "Target FPGA IP address",
        "group": "Target FPGA"
    })
    """Target FPGA IP address"""

    username: Optional[str] = field(metadata={
        "description": "Target FPGA SSH username",
        "group": "Target FPGA"
    })
    """Target FPGA SSH username"""

    password: Optional[str] = field(metadata={
        "description": "Target FPGA SSH password",
        "group": "Target FPGA"
    })
    """Target FPGA SSH password"""

    fpga_workdir: Optional[str] = field(metadata={
        "description": "Target FPGA working directory (WARNING: Files will be transferred and executed in this folder)",
        "group": "Target FPGA"
    })
    """Target FPGA working directory (WARNING: Files will be transferred and executed in this folder)"""
    