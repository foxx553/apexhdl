from pathlib import Path
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

from context import Context
from simulation_registry import SimulationRegistry
from simulation_base import SimulationStage
import utils

@SimulationRegistry.register(predicate=lambda ctx: ctx.simulation_tool == "ghdl", priority=0)
class SimulationGhdl(SimulationStage):
    """
    GHDL simulation stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Get source folder path
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"
        module_file: Path = folder_path / f"{ctx.circuit_name}.vhd"

        # Create sim folder
        sim_folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "sim"
        sim_folder_path.mkdir(parents=True, exist_ok=True)
        results_file: Path = sim_folder_path / f"results_{ctx.circuit_name}.txt"

        # Testbench generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with FPGAEvaluator, a tool created by Florian Delhon and Kevin Peymani
-- Target: {ctx.fpga_board}
-- Module Name: tb_{ctx.circuit_name}
-- Description: Testbench for module {ctx.circuit_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_{ctx.circuit_name} is
end tb_{ctx.circuit_name};

architecture arch_tb_{ctx.circuit_name} of tb_{ctx.circuit_name} is

    signal input_a : STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);
    signal result  : STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);

    file output_file : TEXT open WRITE_MODE is "{str(results_file)}";

begin

    uut : entity work.{ctx.circuit_name}
        generic map (
            DATA_WIDTH => {ctx.data_width}{f",\n\t\t\tSEGMENT_IDX_WIDTH => {ctx.segment_idx_width}" if ctx.method_name == "binary" or ctx.method_name == "hybrid" else ""}{f",\n\t\t\tGROUP_IDX_WIDTH => {ctx.group_idx_width}" if ctx.method_name == "binary" else ""}
        )
        port map (
            input_a => input_a,
            result  => result
        );

    tb_proc: process
        variable line_out : line;
        variable input_str, result_str : string(1 to {ctx.data_width});
    begin
        for i in 0 to 2**{ctx.data_width} - 1 loop
            input_a <= std_logic_vector(to_unsigned(i, {ctx.data_width}));

            wait for 10 ns;

            write(line_out, integer'image(i));
            write(line_out, string'(","));
            write(line_out, integer'image(to_integer(unsigned(result))));
            writeline(output_file, line_out);

        end loop;
        
        std.env.stop(0);
    end process;

end arch_tb_{ctx.circuit_name};
        """

        # VHDL file writing
        tb_file: Path = folder_path / f"tb_{ctx.circuit_name}.vhd"
        tb_file.write_text(vhdl_code)

        # Run GHDL simulation
        Path("./work-obj08.cf").unlink(missing_ok=True) # Note = Delete GHDL work directory to trigger full simulation
        subprocess.run(["ghdl", "-a", "--std=08", module_file, tb_file], capture_output=False, check=True)
        subprocess.run(["ghdl", "-e", "--std=08", f"tb_{ctx.circuit_name}"], capture_output=False, check=True)
        subprocess.run(["ghdl", "-r", "--std=08", f"tb_{ctx.circuit_name}"], capture_output=False, check=True)

        # Validation parameters
        lambda_function: Any = utils.lambdify_function(ctx.math_function)
        x_step = (ctx.x_max - ctx.x_min) / (2 ** ctx.data_width)
        y_step = (ctx.y_max - ctx.y_min) / (2 ** ctx.data_width)
        theoretical_step = 0.001

        # Read results file
        raw_y_values = []
        with results_file.open('r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    raw_y_values.append(int(parts[1]))

        # Computing theoretical and experimental values
        x_values = np.arange(ctx.x_min, ctx.x_max, theoretical_step)
        y_evaluator = []
        y_theoretical = []
        absolute_errors = []
        relative_errors = []
        for x_value in x_values:
            theoretical = lambda_function(x_value)
            evaluator = ctx.y_min + raw_y_values[utils.clamp_nearest(x_value, ctx.x_min, x_step, ctx.data_width)] * y_step
            y_theoretical.append(theoretical)
            y_evaluator.append(evaluator)
            absolute_errors.append(abs(theoretical - evaluator))
            relative_errors.append(0 if theoretical == 0 else abs((theoretical - evaluator) / theoretical))

        # Computing errors, and appending it to the results file
        mean_error = np.mean(absolute_errors)
        max_error = np.max(absolute_errors)
        mean_relative_error = np.mean(relative_errors)
        max_relative_error = np.max(relative_errors)
        with results_file.open('a') as file:
            file.write(f"\n{"{:.3g}".format(max_error)},{"{:.3g}".format(mean_error)}")
            file.write(f"\n{"{:.3g}".format(max_relative_error)},{"{:.3g}".format(mean_relative_error)}")

        # Computing and saving comparison plot
        plt.figure(figsize=(20, 10))
        plt.plot(x_values, y_theoretical, color='blue', linewidth=5, label='Theoretical values')
        plt.plot(x_values, y_evaluator, color='red', linewidth=5, label='Experimental values')
        plt.title('Theoretical values vs. experimental values', fontsize=40)
        plt.xlabel('x', fontsize=30)
        plt.ylabel('Values', fontsize=30)
        plt.grid(True)
        plt.xticks(fontsize=30)
        plt.yticks(fontsize=30)
        plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
        plt.savefig(sim_folder_path / f"curves_{ctx.circuit_name}.png")

        # Computing and saving absolute error plot
        plt.figure(figsize=(20, 10))
        plt.plot(x_values, absolute_errors, color='blue', linewidth=3, label="Absolute errors")
        plt.plot(x_values, [max_error for _ in range(len(x_values))], color='red', linewidth=5, label=f"Max error = {"{:.3g}".format(max_error)}")
        plt.plot(x_values, [mean_error for _ in range(len(x_values))], color='orange', linewidth=5, label=f"Mean error = {"{:.3g}".format(mean_error)}")
        plt.title('Absolute error of evaluator values', fontsize=30)
        plt.xlabel('x', fontsize=30)
        plt.ylabel('Absolute error', fontsize=30)
        plt.grid(True)
        plt.xticks(fontsize=30)
        plt.yticks(fontsize=30)
        plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
        plt.savefig(sim_folder_path / f"error_absolute_{ctx.circuit_name}.png")

        # Computing and saving relative error plot
        plt.figure(figsize=(20, 10))
        plt.plot(x_values, relative_errors, color='blue', linewidth=3, label="Relative errors")
        plt.plot(x_values, [max_relative_error for _ in range(len(x_values))], color='red', linewidth=5, label=f"Max error = {"{:.3g}".format(max_relative_error)}")
        plt.plot(x_values, [mean_relative_error for _ in range(len(x_values))], color='orange', linewidth=5, label=f"Mean error = {"{:.3g}".format(mean_relative_error)}")
        plt.title('Relative error of evaluator values', fontsize=30)
        plt.xlabel('x', fontsize=30)
        plt.ylabel('Relative error', fontsize=30)
        plt.grid(True)
        plt.xticks(fontsize=30)
        plt.yticks(fontsize=30)
        plt.legend(loc='upper center', bbox_to_anchor=(0.95, 0.6), fontsize=25)
        plt.savefig(sim_folder_path / f"error_relative_{ctx.circuit_name}.png")

        return True