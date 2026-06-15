import sys
from pathlib import Path
import subprocess
import re
from re import Match

from apex.context import Context
from apex.synthesis_stage.synthesis_registry import SynthesisRegistry, SynthesisStage
import apex.utils as utils

@SynthesisRegistry.register(predicate=lambda ctx: ctx.step in ["syn", "syn-pnr", "all"] and ctx.eda_tool == "vivado", priority=1)
class SynthesisVivado(SynthesisStage):
    """
    Vivado synthesis stage
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:

        self.logger.info("Starting Vivado synthesis stage...")

        # Preliminary checks
        if ctx.fpga_board is None:
            self.logger.error("Vivado synthesis requires ctx.fpga_board to be set...")
            sys.exit(1)

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

    -- Generated circuit
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

        # Vivado logs target path and command
        log_file: Path = syn_folder_path / "vivado.log"
        cmd: str = f"vivado -mode batch -source {tcl_script} -log {log_file} -tclargs {ctx.fpga_board} {ctx.output_folder} {ctx.circuit_name} {ctx.step}"
        
        self.logger.info(f"Launching Vivado... Follow detailed progress in {str(log_file)}")

        # Vivado execution with errors handling
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=utils.SUBPROCESS_TIMEOUT)
            self.logger.info("Vivado completed successfully!")
        except subprocess.CalledProcessError as e:
            self.logger.error("Vivado failed, please check the log file for details...")
            self.logger.debug(f"Captured error: {e.stderr}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Vivado timed out, exceeding the {utils.SUBPROCESS_TIMEOUT} seconds threshold...")

        metrics_dict: dict[str, float] = {}

        # Parse utilization report, if the file exists
        metrics_dict["LutCount"] = -1
        utilization_file_path: Path = syn_folder_path / f"{ctx.circuit_name}_utilization.rpt"
        if utilization_file_path.exists():
            with utilization_file_path.open('r') as file:
                for line in file:
                    if line.strip().startswith('| top'):
                        parts: list[str] = [p.strip() for p in line.split('|')]
                        metrics_dict["LutCount"] = int(parts[3])
        
        # Parse timing report, if the file exists
        if ctx.step != "syn":
            metrics_dict["CriticalPathLatency (ns)"] = -1
            timing_file_path: Path = syn_folder_path / f"{ctx.circuit_name}_timing.rpt"
            if timing_file_path.exists():
                with timing_file_path.open('r') as file:
                    content: str = file.read()
                    match: Match[str] | None = re.search(r"Data Path Delay:\s+([\d.]+)ns", content)
                    if match:
                        metrics_dict["CriticalPathLatency (ns)"] = float(match.group(1))

        return metrics_dict