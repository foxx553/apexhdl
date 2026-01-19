from pathlib import Path

from evaluator.context import Context
from evaluator.generation_stage.generation_registry import GenerationRegistry
from evaluator.generation_stage.generation_base import GenerationStage
import evaluator.utils as utils

@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "rom", priority=1)
class GenerationRom(GenerationStage):
    """
    ROM generation stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Create folder if necessary
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"
        folder_path.mkdir(parents=True, exist_ok=True)

        # Discrete output calculation
        y_discrete_values: list[int] = utils.compute_discrete_output(
            function_str=ctx.math_function, 
            x_data_width=ctx.data_width, 
            x_min=ctx.x_min, 
            x_max=ctx.x_max, 
            y_data_width=ctx.data_width, 
            y_min=ctx.y_min, 
            y_max=ctx.y_max
        )

        # VHDL behavioral code generation
        rom_code: str = ""
        for x_value, y_value in enumerate(y_discrete_values):
            rom_code += f"\t\t{x_value} => \"{utils.int_to_lsb(y_value, ctx.data_width)}\",\n"
        rom_code += f"\t\tothers => \"{utils.int_to_lsb(0, ctx.data_width)}\""

        # VHDL complete code generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with FPGAEvaluator, a tool created by Florian Delhon and Kevin Peymani
-- Target: {ctx.fpga_board}
-- Module Name: {ctx.circuit_name}
-- Function: f(x) = {ctx.math_function}
-- Evaluator method: ROM
-- Data width: {ctx.data_width} bits
-- Range: x in [{ctx.x_min}; {ctx.x_max}[, y in [{ctx.y_min}; {ctx.y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {ctx.circuit_name} is
    generic (
        DATA_WIDTH : positive := {ctx.data_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {ctx.circuit_name};

architecture arch_{ctx.circuit_name} of {ctx.circuit_name} is
    
    attribute rom_style : string;
    type rom_array_t is array (0 to 2**DATA_WIDTH - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant ROM_VALUES : rom_array_t := (
{rom_code}
    );
    attribute rom_style of ROM_VALUES : constant is "distributed";

begin

    result <= ROM_VALUES(to_integer(unsigned(input_a)));

end arch_{ctx.circuit_name};
        """

        # VHDL file writing
        file_path: Path = folder_path / f"{ctx.circuit_name}.vhd"
        file_path.write_text(vhdl_code)

        return True