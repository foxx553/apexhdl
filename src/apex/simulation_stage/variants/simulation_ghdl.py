from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

from apex.context import Context
from apex.simulation_stage.simulation_registry import SimulationRegistry, SimulationStage
import apex.utils as utils

@SimulationRegistry.register(predicate=lambda ctx: ctx.step == "sim" and ctx.simulation_tool == "ghdl", priority=1)
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
-- Generated with ApexHDL
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

        # Run GHDL simulation, with error handling
        Path("./work-obj08.cf").unlink(missing_ok=True) # Note = Delete GHDL work directory to trigger full simulation
        try:
            subprocess.run(["ghdl", "-a", "--std=08", module_file, tb_file], timeout=300, shell=True, capture_output=True, check=True)
            subprocess.run(["ghdl", "-e", "--std=08", f"tb_{ctx.circuit_name}"], timeout=300, shell=True, capture_output=True, check=True)
            subprocess.run(["ghdl", "-r", "--std=08", f"tb_{ctx.circuit_name}"], timeout=300, shell=True, capture_output=True, text=True)
        except subprocess.TimeoutExpired as e:
            print(f"[ERROR] GHDL execution unsuccessful for circuit {ctx.circuit_name}: 5 minutes timeout")
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(e.pid)], capture_output=True)
            return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] GHDL execution unsuccessful for circuit {ctx.circuit_name}: {e}")
            return False

        # Validation parameters
        lambda_function: Any = utils.lambdify_function(ctx.math_function)
        x_step: float = (ctx.x_max - ctx.x_min) / (2 ** ctx.data_width)
        y_step: float = (ctx.y_max - ctx.y_min) / (2 ** ctx.data_width)
        theoretical_step: float = 0.001

        # Read results file
        raw_y_values: list[int] = []
        with results_file.open('r') as file:
            for line in file:
                parts: list[str] = line.strip().split(',')
                if len(parts) == 2:
                    raw_y_values.append(int(parts[1]))

        # Computing theoretical and experimental values
        x_values: list[float] = np.arange(ctx.x_min, ctx.x_max, theoretical_step)
        y_evaluator: list[float] = []
        y_theoretical: list[float] = []
        absolute_errors: list[float] = []
        relative_errors: list[float] = []
        for x_value in x_values:
            theoretical: float = lambda_function(x_value)
            evaluator: float = ctx.y_min + raw_y_values[utils.clamp_nearest(x_value, ctx.x_min, x_step, ctx.data_width)] * y_step
            y_theoretical.append(theoretical)
            y_evaluator.append(evaluator)
            absolute_errors.append(abs(theoretical - evaluator))
            relative_errors.append(0 if theoretical == 0 else abs((theoretical - evaluator) / theoretical))

        # Computing errors, and appending it to the results file
        mean_error: float = np.mean(absolute_errors)
        max_error: float = np.max(absolute_errors)
        mean_relative_error: float = np.mean(relative_errors)
        max_relative_error: float = np.max(relative_errors)
        with results_file.open('a') as file:
            file.write(f"\n{"{:.3g}".format(max_error)},{"{:.3g}".format(mean_error)}")
            file.write(f"\n{"{:.3g}".format(max_relative_error)},{"{:.3g}".format(mean_relative_error)}")

        # Computing and saving comparison plot
        utils.generate_apex_plot(
            x_values, 
            {
                "Theoretical": (y_theoretical, "blue"),
                "Experimental": (y_evaluator, "red")
            },
            sim_folder_path / f"curves_{ctx.circuit_name}.svg",
            "Theoretical vs. experimental values",
            "Output"
        )

        # Computing and saving absolute error plot
        utils.generate_apex_plot(
            x_values, 
            {
                "Absolute errors": (absolute_errors, "blue"),
                f"Max error = {"{:.3g}".format(max_error)}": ([max_error for _ in range(len(x_values))], "red"),
                f"Mean error = {"{:.3g}".format(mean_error)}": ([mean_error for _ in range(len(x_values))], "orange")
            },
            sim_folder_path / f"error_absolute_{ctx.circuit_name}.svg",
            "Absolute errors",
            "Error"
        )

        # Computing and saving relative error plot
        utils.generate_apex_plot(
            x_values, 
            {
                "Relative errors": (relative_errors, "blue"),
                f"Max error = {"{:.3g}".format(max_relative_error)}": ([max_relative_error for _ in range(len(x_values))], "red"),
                f"Mean error = {"{:.3g}".format(mean_relative_error)}": ([mean_relative_error for _ in range(len(x_values))], "orange")
            },
            sim_folder_path / f"error_relative_{ctx.circuit_name}.svg",
            "Relative errors",
            "Error"
        )

        return True