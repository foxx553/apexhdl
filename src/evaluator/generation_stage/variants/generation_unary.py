from pathlib import Path

from context import Context
from generation_registry import GenerationRegistry
from generation_base import GenerationStage
import utils

@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "unary", priority=1)
class GenerationUnary(GenerationStage):
    """
    Unary generation stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Create folder if necessary
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"
        folder_path.mkdir(parents=True, exist_ok=True)

        # Discrete output calculation
        y_discrete_values: list[int] = utils.compute_discrete_output(ctx.math_function, ctx.data_width, ctx.x_min, ctx.x_max, ctx.data_width, ctx.y_min, ctx.y_max)

        # Computing unary core routing logic
        unary_core_array: list[list[int]] = [[-1] for _ in range(2**ctx.data_width)]
        for output_value in range(2**ctx.data_width):
            for x_value, y_value in enumerate(y_discrete_values):
                if y_value == output_value:
                    if unary_core_array[output_value][0] == -1:
                        unary_core_array[output_value][0] = x_value
                    else:
                        unary_core_array[output_value].append(x_value)
        
        # Converting routing logic to VHDL code
        unary_core_code: str = ""
        for output_value in range(len(unary_core_array)):
            if unary_core_array[output_value][0] != -1:
                for index, x_value in enumerate(unary_core_array[output_value]):
                    if index == 0:
                        unary_core_code += f"\tdecoder_input({output_value}) <= encoder_output({x_value})"
                    else:
                        unary_core_code += f" or encoder_output({x_value})"
                unary_core_code += ";\n"

        # VHDL complete code generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with FPGAEvaluator, a tool created by Florian Delhon and Kevin Peymani
-- Target: {ctx.fpga_board}
-- Module Name: {ctx.circuit_name}
-- Function: f(x) = {ctx.math_function}
-- Evaluator method: Unary
-- Data width: {ctx.data_width} bits
-- Range: x in [{ctx.x_min};{ctx.x_max}[, y in [{ctx.y_min};{ctx.y_max}[
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

    signal encoder_output: STD_LOGIC_VECTOR(2**DATA_WIDTH - 1 downto 0);
    signal decoder_input: STD_LOGIC_VECTOR(2**DATA_WIDTH - 1 downto 0);

begin

    -- One-hot encoder    
    one_hot_encoder: process(input_a)
    begin
        encoder_output <= (others => '0');
        encoder_output(to_integer(unsigned(input_a))) <= '1';
    end process one_hot_encoder;

    -- Unary code
{unary_core_code}

    -- One-hot decoder
    one_hot_decoder: process(decoder_input)
    begin
        result <= (others => '0');
        for i in 0 to decoder_input'length - 1 loop
            if decoder_input(i) = '1' then
                result <= std_logic_vector(to_unsigned(i, result'length));
            end if;
        end loop;
    end process one_hot_decoder;

end arch_{ctx.circuit_name};
        """

        # VHDL file writing
        file_path: Path = folder_path / f"{ctx.circuit_name}.vhd"
        file_path.write_text(vhdl_code)

        return True