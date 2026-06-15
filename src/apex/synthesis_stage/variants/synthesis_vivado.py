from pathlib import Path
import subprocess
import re
from re import Match

from apex.context import Context
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry, SynthesisStage

@SynthesisRegistry.register(predicate=lambda ctx: ctx.step in ["syn", "syn-pnr", "all"] and ctx.eda_tool == "vivado", priority=1)
class SynthesisVivado(SynthesisStage):
    """
    Vivado synthesis stage
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:

        # Preliminary checks
        if ctx.fpga_board is None:
            raise ValueError("Vivado synthesis requires ctx.fpga_board to be set")

        # Get source folder path
        folder_path: Path = ctx.output_folder / ctx.circuit_name / "vhdl"

        # Get TCL script path
        tcl_script: Path = Path("../tcl/analyze_evaluator.tcl")

        # Create syn folder
        syn_folder_path: Path = ctx.output_folder / ctx.circuit_name / "syn"
        syn_folder_path.mkdir(parents=True, exist_ok=True)

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
        log_file: Path = syn_folder_path / "vivado.log"

        # Vivado execution in batch mode
        cmd: str = f"vivado -mode batch -source {tcl_script} -log {log_file} -tclargs {ctx.fpga_board} {ctx.output_folder} {ctx.circuit_name} {ctx.step}"
        subprocess.run(cmd, shell=True, text=True)

        metrics_dict: dict[str, float] = {}

        # Parse utilization report, if the file exists
        utilization_file_path: Path = syn_folder_path / f"{ctx.circuit_name}_utilization.rpt"
        if utilization_file_path.exists():
            with utilization_file_path.open('r') as file:
                for line in file:
                    if line.strip().startswith('| top'):
                        parts: list[str] = [p.strip() for p in line.split('|')]
                        metrics_dict["LutCount"] = int(parts[3])
        
        # Parse timing report, if the file exists
        timing_file_path: Path = syn_folder_path / f"{ctx.circuit_name}_timing.rpt"
        if timing_file_path.exists():
            with timing_file_path.open('r') as file:
                content: str = file.read()
                match: Match[str] | None = re.search(r"Data Path Delay:\s+([\d.]+)ns", content)
                if match:
                    metrics_dict["CriticalPathLatency"] = float(match.group(1))

        return metrics_dict