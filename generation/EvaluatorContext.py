from dataclasses import dataclass
from typing import Any

@dataclass
class EvaluatorContext:
    """
    Context of the approximator's generation

    Attributes:
        method_name (str): Name of the circuit generation method
        circuit_name (str): Name of the circuit generated
        output_folder_path (str): Folder where all generated files will be put 

        math_function (Any): Mathematical function to be approximated by the generated circuit
        x_min (float): Minimum X value of the approximation region
        x_max (float): Maximum X value of the approximation region
        y_min (float): Minimum Y value of the approximation region
        y_max (float): Maximum Y value of the approximation region

        data_width (int): Number of bits of the approximation
        segment_idx_width (int): Number of bits for indexing segments (if applicable)
        group_idx_width (int): Number of bits for indexing groups of segments (if applicable)

        fpga_board (str): Part number of the target FPGA
        analysis_contraints_file_path (str): XDC file containing hardware constraints for the standalone analysis
        implementation_constraints_file_path (str): XDC file containing hardware constraints for the complete implementation
        design_wrapper_file_path (str): TCL file containing the TCL procedure which will wrap the generated circuit

        ip_address (str): IP address for SSH connection to the target FPGA
        username (str): Username for SSH connection to the target FPGA
        password (str): Password for SSH connection to the target FPGA
        fpga_working_folder_path (str): Folder on the target FPGA in which all files will be sent and executed
        pynq_venv_setup_script_path (str): Shell script of the PYNQ image which activates the Python Virtual Environment
        xilinx_runtime_script_path (str): Shell script of the PYNQ image which sets up the necessary environment variables for the Xilinx Run Time
    """
    
    # General
    method_name: str
    circuit_name: str
    output_folder_path: str

    # Maths
    math_function: Any
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    # Generation
    data_width: int
    segment_idx_width: int
    group_idx_width: int

    # Hardware
    fpga_board: str
    analysis_contraints_file_path: str
    implementation_constraints_file_path: str
    design_wrapper_file_path: str

    # SSH
    ip_address: str
    username: str
    password: str
    fpga_working_folder_path: str
    pynq_venv_setup_script_path: str
    xilinx_runtime_script_path: str
    