from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import shutil

from apex.context import Context
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry, SynthesisStage

@SynthesisRegistry.register(predicate=lambda ctx: "rpt" in ctx.step and ctx.synthesis_tool == "vivado", priority=1)
class SynthesisVivado(SynthesisStage):
    """
    Vivado synthesis stage
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
-- Generated with ApexHDL
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
        port map (
            input_a => input_a,
            result  => result
        );
end arch_top_{ctx.circuit_name};
        """

        # VHDL file writing
        top_file: Path = folder_path / f"top_{ctx.circuit_name}.vhd"
        top_file.write_text(vhdl_code)

        # Vivado logs target path
        log_file: Path = rpt_folder_path / "vivado.log"
        jou_file: Path = rpt_folder_path / "vivado.jou"

        # Vivado execution in batch mode
        cmd = [
            "vivado",
            "-mode", "batch",
            "-source", tcl_script,
            "-log", log_file,
            "-journal", jou_file,
            "-tclargs", ctx.fpga_board, ctx.output_folder_path, ctx.circuit_name, ctx.step
        ]

        # Error handling
        try:
            subprocess.run(cmd, timeout=900, shell=True, text=True)
        except subprocess.TimeoutExpired:
            print(f"[ERROR] Vivado synthesis unsuccessful for circuit {ctx.circuit_name}: 15 minutes timeout")
            subprocess.run(["taskkill", "/F", "/T", "/IM", "vivado.exe"], capture_output=True)
            return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Vivado synthesis unsuccessful for circuit {ctx.circuit_name}: {e}")
            return False

        return True