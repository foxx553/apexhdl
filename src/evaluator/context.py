from dataclasses import dataclass
from typing import Any, Optional
from pathlib import Path

@dataclass
class Context:
    """
    Context of the approximator's generation

    Attributes:
        method_name (str): Name of the circuit generation method
        circuit_name (str): Name of the circuit generated
        output_folder_path (Path): Folder where all generated files will be put 

        math_function (str): Mathematical function to be approximated by the generated circuit
        x_min (float): Minimum X value of the approximation region
        x_max (float): Maximum X value of the approximation region
        y_min (float): Minimum Y value of the approximation region
        y_max (float): Maximum Y value of the approximation region

        data_width (int): Number of bits of the approximation
        segment_idx_width (Optional[int]): Number of bits for indexing segments (if applicable)
        group_idx_width (Optional[int]): Number of bits for indexing groups of segments (if applicable)

        simulation_tool (Optional[str]): Software used for circuit simulation
        analysis_tool (Optional[str]): Software used for circuit analysis
        implementation_tool (Optional[str]): Software used for circuit implementation and bitstream generation
        
        fpga_board (Optional[str]): Part number of the target FPGA
        ip_address (Optional[str]): IP address for SSH connection to the target FPGA
        username (Optional[str]): Username for SSH connection to the target FPGA
        password (Optional[str]): Password for SSH connection to the target FPGA
        fpga_working_folder_path (Optional[str]): Folder on the target FPGA in which all files will be sent and executed
        pynq_venv_setup_script_path (Optional[str]): Shell script of the PYNQ image which activates the Python Virtual Environment
        xilinx_runtime_script_path (Optional[str]): Shell script of the PYNQ image which sets up the necessary environment variables for the Xilinx Run Time
    """
    
    # General
    method_name: str
    circuit_name: str
    output_folder_path: Path

    # Maths
    math_function: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    # Generation
    data_width: int
    segment_idx_width: Optional[int]
    group_idx_width: Optional[int]

    # Software
    simulation_tool: Optional[str]
    analysis_tool: Optional[str]
    implementation_tool: Optional[str]

    # Hardware
    fpga_board: Optional[str]
    ip_address: Optional[str]
    username: Optional[str]
    password: Optional[str]
    fpga_working_folder_path: Optional[str]
    pynq_venv_setup_script_path: Optional[str]
    xilinx_runtime_script_path: Optional[str]
    