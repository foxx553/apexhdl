from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class Context:
    """
    Context of the approximator's generation
    """
    
    # General
    method_name: str
    """Name of the circuit generation method"""

    circuit_name: str
    """Name of the circuit generated"""

    output_folder_path: Path
    """Folder where all generated files will be put"""

    step: str
    """Steps done for the generation (sim = simulation-only, rpt = analysis after synthesis, rpt = analysis after place/route, impl = implementation)"""

    # Maths
    math_function: str
    """Mathematical function to be approximated by the generated circuit"""

    x_min: float
    """Minimum X value of the approximation region"""

    x_max: float
    """Maximum X value of the approximation region"""

    y_min: float
    """Minimum Y value of the approximation region"""

    y_max: float
    """Maximum Y value of the approximation region"""

    # Generation
    data_width: int
    """Number of bits of the approximation"""

    segment_idx_width: Optional[int] = None
    """Number of bits for indexing segments (if applicable)"""

    group_idx_width: Optional[int] = None
    """Number of bits for indexing groups of segments (if applicable)"""

    # Software
    simulation_tool: Optional[str] = None
    """Software used for circuit simulation"""

    analysis_tool: Optional[str] = None
    """Software used for circuit analysis"""

    implementation_tool: Optional[str] = None
    """Software used for circuit implementation and bitstream generation"""
    
    # Hardware
    fpga_board: Optional[str] = None
    """Part number of the target FPGA"""

    ip_address: Optional[str] = None
    """IP address for SSH connection to the target FPGA"""

    username: Optional[str] = None
    """Username for SSH connection to the target FPGA"""

    password: Optional[str] = None
    """Password for SSH connection to the target FPGA"""

    fpga_working_folder_path: Optional[str] = None
    """Folder on the target FPGA in which all files will be sent and executed"""
    