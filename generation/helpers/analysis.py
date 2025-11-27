import subprocess
import shutil
import os

def generate_top(evaluator_type, args):
    """ Generates the top module for Vivado synthesis """

    # Args extraction
    evaluator_name = args[0]
    data_width = int(args[2])
    segment_idx_width, group_idx_width = 0, 0
    if evaluator_type == "binary" or evaluator_type == "hybrid":
        segment_idx_width = int(args[7])
        if evaluator_type == "binary":
            group_idx_width = int(args[8]) 

    return f"""
-------------------------------------
-- Engineers: Florian Delhon, Kevin Peymani
-- Target: PYNQ-Z2
-- Module Name: top_{evaluator_name}
-- Description: Top module for {evaluator_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity top_{evaluator_name} is
    port (
        input_a : in STD_LOGIC_VECTOR({data_width - 1} downto 0);
        result  : out STD_LOGIC_VECTOR({data_width - 1} downto 0)
    );
end top_{evaluator_name};

architecture arch_top_{evaluator_name} of top_{evaluator_name} is
begin
    uut : entity work.{evaluator_name}
        generic map (
            DATA_WIDTH => {data_width}{f",\n\t\t\tSEGMENT_IDX_WIDTH => {segment_idx_width}" if evaluator_type == "binary" or evaluator_type == "hybrid" else ""}{f",\n\t\t\tGROUP_IDX_WIDTH => {group_idx_width}" if evaluator_type == "binary" else ""}
        )
        port map (
            input_a => input_a,
            result  => result
        );
end arch_top_{evaluator_name};
"""

def run_vivado_analysis(evaluator_name, run_mode):
    """Run Vivado TCL script and capture results"""
    
    # Vivado execution in batch mode
    cmd = [
        "vivado",
        "-mode", "batch",
        "-source", "../implementation/tcl/analyze_evaluator.tcl",
        "-tclargs", evaluator_name, run_mode
    ]
    result = subprocess.run(cmd, shell=True, text=True)
    if os.path.exists(f"../output/{evaluator_name}/rpt/vivado.log"):
        os.remove(f"../output/{evaluator_name}/rpt/vivado.log")
    shutil.move("vivado.log", f"../output/{evaluator_name}/rpt/")
    
    if result.returncode != 0:
        print(f"Error running Vivado for {evaluator_name}:")
        print(result.stderr)
        return None