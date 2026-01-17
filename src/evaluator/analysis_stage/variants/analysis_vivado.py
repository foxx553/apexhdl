from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import shutil

from context import Context
from analysis_registry import AnalysisRegistry
from analysis_base import AnalysisStage

@AnalysisRegistry.register(predicate=lambda ctx: ctx.analysis_tool == "vivado", priority=1)
class AnalysisVivado(AnalysisStage):
    """
    Vivado analysis stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Get source folder path
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"

        # Get TCL script path
        tcl_script: Path = Path("../tcl/analyze_evaluator.tcl")

        # Create rpt folder
        rpt_folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "rpt"
        rpt_folder_path.mkdir(parents=True, exist_ok=True)

        # Top file generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with FPGAEvaluator, a tool created by Florian Delhon and Kevin Peymani
-- Target: {ctx.fpga_board}
-- Module Name: top_{ctx.circuit_name}
-- Description: Top module for {ctx.circuit_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity top_{ctx.circuit_name} is
    port (
        input_a : in STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);
        result  : out STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0)
    );
end top_{ctx.circuit_name};

architecture arch_top_{ctx.circuit_name} of top_{ctx.circuit_name} is
begin
    uut : entity work.{ctx.circuit_name}
        generic map (
            DATA_WIDTH => {ctx.data_width}{f",\n\t\t\tSEGMENT_IDX_WIDTH => {ctx.segment_idx_width}" if ctx.method_name == "bipartite" or ctx.method_name == "hybrid" else ""}{f",\n\t\t\tGROUP_IDX_WIDTH => {ctx.group_idx_width}" if ctx.method_name == "bipartite" else ""}
        )
        port map (
            input_a => input_a,
            result  => result
        );
end arch_top_{ctx.circuit_name};
        """

        # VHDL file writing
        top_file: Path = folder_path / f"top_{ctx.circuit_name}.vhd"
        top_file.write(vhdl_code)

        # Vivado execution in batch mode
        cmd = [
            "vivado",
            "-mode", "batch",
            "-source", tcl_script,
            "-tclargs", ctx.fpga_board, ctx.output_folder_path, ctx.circuit_name, ctx.analysis_mode
        ]
        vivado_result: CompletedProcess[str] = subprocess.run(cmd, shell=True, text=True)

        # Error handling
        if vivado_result.returncode != 0:
            print(f"[ERROR] Vivado analysis unsuccessful for circuit {ctx.circuit_name}: {vivado_result.stderr}")
            return False
        
        # Removing old logs and putting in new Vivado logs
        Path(rpt_folder_path / "vivado.log").unlink(missing_ok=True)
        shutil.move("vivado.log", rpt_folder_path)

        return True