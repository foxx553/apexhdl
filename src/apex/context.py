from dataclasses import dataclass, field
from typing import Optional, Literal 
from pathlib import Path

@dataclass
class Context:
    """
    Context of the ApexHDL execution
    """
    
    # General
    method_name: list[Literal["rom", "unary", "hybrid", "bipartite", "symmetric"]] = field(
        metadata={"help": "Name of the circuit generation method(s): rom = Single ROM, unary = Purely Unary, hybrid = Hybrid Binary/Unary, bipartite = Bipartite, symmetric = Symmetric Bipartite", "group": "General"}
    )
    """Name of the circuit generation method(s): rom = Single ROM, unary = Purely Unary, hybrid = Hybrid Binary/Unary, bipartite = Bipartite, symmetric = Symmetric Bipartite"""

    circuit_name: str = field(
        metadata={"help": "Name of the generated circuit(s)", "group": "General"}
    )
    """Name of the generated circuit(s)"""

    output_folder_path: Path = field(
        metadata={"help": "Folder containing all generated artifacts", "group": "General"}
    )
    """Folder containing all generated artifacts"""

    step: Literal["sim", "rpt-synth", "rpt", "impl"] = field(
        metadata={"help": "Executed stages: sim = simulation, rpt-synth = reporting after synthesis, rpt = reporting after place-and-route, impl = on-chip validation", "group": "General"}
    )
    """Executed stages: sim = simulation, rpt-synth = reporting after synthesis, rpt = reporting after place-and-route, impl = on-chip validation"""

    # Maths
    math_function: list[str] = field(
        metadata={"help": "Mathematical function(s) to be approximated", "group": "Maths"}
    )
    """Mathematical function(s) to be approximated"""

    x_min: float = field(
        metadata={"help": "Minimum X value", "group": "Maths"}
    )
    """Minimum X value"""

    x_max: float = field(
        metadata={"help": "Maximum X value", "group": "Maths"}
    )
    """Maximum X value"""

    y_min: float = field(
        metadata={"help": "Minimum Y value", "group": "Maths"}
    )
    """Minimum Y value"""

    y_max: float = field(
        metadata={"help": "Maximum Y value", "group": "Maths"}
    )
    """Maximum Y value"""

    # Bit-precision
    data_width: list[int] = field(
        metadata={"help": "Word length(s) of input/output values", "group": "Bit-precision"}
    )
    """Word length(s) of input/output values"""

    segment_idx_width: Optional[int] = field(
        metadata={"help": "Bits indexing segments", "group": "Bit-precision"}
    )
    """Bits indexing segments (for hybrid, bipartite, and symmetric)"""

    group_idx_width: Optional[int] = field(
        metadata={"help": "Bits indexing group of segments", "group": "Bit-precision"}
    )
    """Bits indexing group of segments (for bipartite, and symmetric)"""

    # Tools
    simulation_tool: Optional[Literal["ghdl"]] = field(
        metadata={"help": "Tool used for behavorial simulation: ghdl = GHDL", "group": "Tools"}
    )
    """Tool used for behavorial simulation: ghdl = GHDL"""

    synthesis_tool: Optional[Literal["vivado"]] = field(
        metadata={"help": "Tool used for the synthesis: vivado = Vivado", "group": "Tools"}
    )
    """Tool used for the synthesis: vivado = Vivado"""

    implementation_tool: Optional[Literal["vivado"]] = field(
        metadata={"help": "Tool used for the wrapping and bitstream generation: vivado = Vivado", "group": "Tools"}
    )
    """Tool used for the wrapping and bitstream generation: vivado = Vivado"""
    
    # Target FPGA
    fpga_board: Optional[Literal["xc7z020clg400-1"]] = field(
        metadata={"help": "Target FPGA part number: xc7z020clg400-1 = PYNQ-Z2", "group": "Target FPGA"}
    )
    """Target FPGA part number: xc7z020clg400-1 = PYNQ-Z2"""

    ip_address: Optional[str] = field(
        metadata={"help": "Target FPGA IP address", "group": "Target FPGA"}
    )
    """Target FPGA IP address"""

    username: Optional[str] = field(
        metadata={"help": "Target FPGA SSH username", "group": "Target FPGA"}
    )
    """Target FPGA SSH username"""

    password: Optional[str] = field(
        metadata={"help": "Target FPGA SSH password", "group": "Target FPGA"}
    )
    """Target FPGA SSH password"""

    fpga_working_folder_path: Optional[str] = field(
        metadata={"help": "Target FPGA working directory (WARNING: Files will be transferred and executed in this folder)", "group": "Target FPGA"}
    )
    """Target FPGA working directory (WARNING: Files will be transferred and executed in this folder)"""
    