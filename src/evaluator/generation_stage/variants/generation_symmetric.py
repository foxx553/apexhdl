from pathlib import Path
from typing import Any

from context import Context
from generation_registry import GenerationRegistry
from generation_base import GenerationStage
import utils

@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "symmetric", priority=1)
class GenerationSymmetric(GenerationStage):
    """
    Symmetric bipartite generation stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Create folder if necessary
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"
        folder_path.mkdir(parents=True, exist_ok=True)

        # Offset table and Input table calculations
        lambda_function: Any = utils.lambdify_function(ctx.math_function)
        offset_table: list[int] = []
        input_table: list[int] = []
        delta_x_group: float = (ctx.x_max - ctx.x_min) / 2**ctx.group_idx_width
        delta_x_segment: float = (ctx.x_max - ctx.x_min) / 2**ctx.segment_idx_width
        y_step: float = (ctx.y_max - ctx.y_min) / 2**ctx.data_width
        for group_idx in range(2**ctx.group_idx_width):
            delta_y_group: float = lambda_function((group_idx + 1) * delta_x_group + ctx.x_min) - lambda_function(group_idx * delta_x_group + ctx.x_min)
            group_slope: float = delta_y_group / delta_x_group
            segment_y_offset: float = group_slope * (delta_x_segment / 2)
            offset_table += utils.compute_relative_discrete_output(f"{group_slope}*x", ctx.data_width - ctx.segment_idx_width - 1, 0, delta_x_segment / 2, ctx.data_width, (ctx.y_min - ctx.y_max) / 2, (ctx.y_max - ctx.y_min) / 2, segment_y_offset)

            for segment_idx in range(2**(ctx.segment_idx_width-ctx.group_idx_width)):
                x_start_segment: float = group_idx * delta_x_group + segment_idx * delta_x_segment + ctx.x_min
                x_middle_segment: float = x_start_segment + delta_x_segment / 2
                y_middle_segment: float = lambda_function(x_middle_segment)
                input_table.append(utils.clamp_nearest(y_middle_segment, ctx.y_min, y_step, ctx.data_width))

        # VHDL behavioral code generation
        offset_code: str = ""
        for x_value, y_value in enumerate(offset_table):
            offset_code += f"\t\t{x_value} => \"{utils.int_to_lsb(y_value, ctx.data_width)}\",\n"
        offset_code += f"\t\tothers => \"{utils.int_to_lsb(0, ctx.data_width)}\""
        input_code: str = ""
        for x_value, y_value in enumerate(input_table):
            input_code += f"\t\t{x_value} => \"{utils.int_to_lsb(y_value, ctx.data_width)}\",\n"
        input_code += f"\t\tothers => \"{utils.int_to_lsb(0, ctx.data_width)}\""

        # VHDL complete code generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with FPGAEvaluator, a tool created by Florian Delhon and Kevin Peymani
-- Target: {ctx.fpga_board}
-- Module Name: {ctx.evaluator_name}
-- Function: f(x) = {ctx.math_function}
-- Evaluator method: Symmetric
-- Data width: {ctx.data_width} bits
-- Group index width: {ctx.group_idx_width} bits
-- Segment index width: {ctx.segment_idx_width} bits
-- Range: x in [{ctx.x_min}; {ctx.x_max}[, y in [{ctx.y_min}; {ctx.y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {ctx.evaluator_name} is
    generic (
        DATA_WIDTH : positive := {ctx.data_width};
        GROUP_IDX_WIDTH : positive := {ctx.group_idx_width};
        SEGMENT_IDX_WIDTH : positive := {ctx.segment_idx_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {ctx.evaluator_name};

architecture arch_{ctx.evaluator_name} of {ctx.evaluator_name} is
    
    attribute rom_style : string;
    signal offset_entry_lower : STD_LOGIC_VECTOR(DATA_WIDTH - SEGMENT_IDX_WIDTH - 2 downto 0);
    signal offset_entry_lower_raw : STD_LOGIC_VECTOR(DATA_WIDTH - SEGMENT_IDX_WIDTH - 2 downto 0);
    signal offset_entry : STD_LOGIC_VECTOR(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH - 2 downto 0);
    signal offset_value_raw : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal offset_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal input_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal invert : STD_LOGIC;
    
    -- Offset table
    type offset_array_t is array (0 to 2**(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH - 1) - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant OFFSET_TABLE : offset_array_t := (
{offset_code}
    );
    attribute rom_style of OFFSET_TABLE : constant is "distributed";

    -- Input table
    type input_array_t is array (0 to 2**SEGMENT_IDX_WIDTH - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant INPUT_TABLE : input_array_t := (
{input_code}
    );
    attribute rom_style of INPUT_TABLE : constant is "distributed";
    
begin

    invert <= input_a(DATA_WIDTH - SEGMENT_IDX_WIDTH - 1);

    offset_entry_lower_raw <= input_a(DATA_WIDTH - SEGMENT_IDX_WIDTH - 2 downto 0);
    offset_entry_lower <= offset_entry_lower_raw when invert = '0' else not offset_entry_lower_raw;

    offset_entry <= input_a(DATA_WIDTH - 1 downto DATA_WIDTH - GROUP_IDX_WIDTH) & offset_entry_lower;

    offset_value_raw <= OFFSET_TABLE(to_integer(unsigned(offset_entry)));
    offset_value <= offset_value_raw when invert = '0' else not offset_value_raw;

    input_value <= INPUT_TABLE(to_integer(unsigned(input_a(DATA_WIDTH - 1 downto DATA_WIDTH - SEGMENT_IDX_WIDTH))));

    adder: process(input_value, offset_value)
        variable sum : signed(DATA_WIDTH + 1 downto 0);
    begin
        if invert = '0' then
            sum := resize(signed(offset_value), DATA_WIDTH + 2) + signed(resize(unsigned(input_value), DATA_WIDTH + 2));
        else
            sum := resize(signed(offset_value), DATA_WIDTH + 2) + signed(resize(unsigned(input_value), DATA_WIDTH + 2) + 1);
        end if;
        if sum(DATA_WIDTH + 1) = '1' then
            result <= (others => '0');
        elsif sum(DATA_WIDTH) = '1' then
            result <= (others => '1');
        else
            result <= std_logic_vector(sum(DATA_WIDTH - 1 downto 0));
        end if;
    end process adder;

end arch_{ctx.evaluator_name};
        """

        # VHDL file writing
        file_path: Path = folder_path / f"{ctx.circuit_name}.vhd"
        file_path.write_text(vhdl_code)

        return True