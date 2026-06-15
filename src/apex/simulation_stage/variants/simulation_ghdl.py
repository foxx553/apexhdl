from pathlib import Path
import subprocess

from apex.context import Context
from apex.simulation_stage.simulation_registry import SimulationRegistry, SimulationStage
import apex.utils as utils

@SimulationRegistry.register(predicate=lambda ctx: ctx.sim_tool == "ghdl", priority=1)
class SimulationGhdl(SimulationStage):
    """
    GHDL simulation stage
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:

        self.logger.info("Starting GHDL simulation stage...")

        # Get source folder path
        folder_path: Path = ctx.output_folder / ctx.circuit_name / "vhdl"
        module_file: Path = folder_path / f"{ctx.circuit_name}.vhd"

        # Create sim folder
        sim_folder_path: Path = ctx.output_folder / ctx.circuit_name / "sim"
        sim_folder_path.mkdir(parents=True, exist_ok=True)
        outputs_file: Path = sim_folder_path / f"outputs_{ctx.circuit_name}.csv"

        # Testbench generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with ApexHDL
-- Module Name: tb_{ctx.circuit_name}
-- Description: Testbench for circuit {ctx.circuit_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_{ctx.circuit_name} is
end tb_{ctx.circuit_name};

architecture arch_tb_{ctx.circuit_name} of tb_{ctx.circuit_name} is

    signal input_a      : STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);
    signal result       : STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);

    file result_file    : TEXT open WRITE_MODE is "{str(outputs_file)}";

begin

    -- Generated circuit
    uut : entity work.{ctx.circuit_name}
        port map (
            input_a => input_a,
            result  => result
        );

    -- Exhaustive stimuli process
    tb_proc : process
        variable line_out : line;
    begin
        for i in 0 to 2**{ctx.data_width} - 1 loop
            input_a <= std_logic_vector(to_unsigned(i, {ctx.data_width}));

            wait for 10 ns;

            write(line_out, to_string(i) & "," & to_string(to_integer(unsigned(result))));
            writeline(result_file, line_out);
        
        end loop;
        
        std.env.stop(0);
    end process;

end arch_tb_{ctx.circuit_name};
        """

        # VHDL file writing
        tb_file: Path = folder_path / f"tb_{ctx.circuit_name}.vhd"
        tb_file.write_text(vhdl_code)

        # Delete GHDL work directory to trigger full simulation
        Path("./work-obj08.cf").unlink(missing_ok=True) 

        # Run GHDL simulation, with error handling
        subprocess.run(f"ghdl -a --std=08 {module_file} {tb_file}", shell=True, capture_output=True, check=True, timeout=utils.SUBPROCESS_TIMEOUT)
        subprocess.run(f"ghdl -e --std=08 tb_{ctx.circuit_name}", shell=True, capture_output=True, check=True, timeout=utils.SUBPROCESS_TIMEOUT)
        subprocess.run(f"ghdl -r --std=08 tb_{ctx.circuit_name}", shell=True, capture_output=True, text=True, timeout=utils.SUBPROCESS_TIMEOUT)

        # Perform outputs results processing
        mean_absolute_error, max_absolute_error, mean_relative_error, max_relative_error = utils.process_outputs_file(
            outputs_file,
            sim_folder_path,
            ctx.circuit_name,
            utils.lambdify_function(ctx.math_function),
            ctx.data_width,
            ctx.x_min,
            ctx.x_max,
            ctx.y_min,
            ctx.y_max,
            is_simulation=True
        )

        return {
            "SimMaxAbsError": max_absolute_error,
            "SimMeanAbsError": mean_absolute_error,
            "SimMaxRelError": max_relative_error,
            "SimMeanRelError": mean_relative_error
        }