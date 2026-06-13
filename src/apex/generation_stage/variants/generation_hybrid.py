from pathlib import Path
import math

from apex.context import Context
from apex.generation_stage.generation_registry import GenerationRegistry, GenerationStage
import apex.utils as utils

@GenerationRegistry.register(predicate=lambda ctx: ctx.method_name == "hybrid", priority=1)
class GenerationHybrid(GenerationStage):
    """
    Hybrid binary/unary generation stage
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:

        # Create folder if necessary
        folder_path: Path = ctx.output_folder / ctx.circuit_name / "vhdl"
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # If necessary, putting default values for group and segment indexes
        ctx.segmentid_width = ctx.segmentid_width if ctx.segmentid_width is not None else math.ceil(ctx.data_width / 2)

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

        # Division in subfunctions
        segment_width: int = ctx.data_width - ctx.segmentid_width
        subfunctions: list[list[int]] = [[0 for _ in range(2**segment_width)] for _ in range(2**ctx.segmentid_width)]
        biases: list[int] = []
        largest_core_value: int = 0
        for i in range(2**ctx.segmentid_width):
            current_array: list[int] = y_discrete_values[i * 2**segment_width:(i + 1) * 2**segment_width]
            current_bias: int = min(current_array)
            biases.append(current_bias)
            subfunctions[i] = [y - current_bias for y in current_array]
            largest_core_value: int = max(subfunctions[i]) if max(subfunctions[i]) > largest_core_value else largest_core_value
        core_output_width: int = math.ceil(math.log2(largest_core_value))
        
        # Computing unary core routing logic
        unary_core_array: list[list[list[int]]] = [[[-1] for _ in range(2**core_output_width)] for _ in range(2**ctx.segmentid_width)]
        for segment_idx, discrete_values in enumerate(subfunctions):
            for output_value in range(2**core_output_width):
                for x_value, y_value in enumerate(discrete_values):
                    if y_value == output_value:
                        if unary_core_array[segment_idx][output_value][0] == -1:
                            unary_core_array[segment_idx][output_value][0] = x_value
                        else:
                            unary_core_array[segment_idx][output_value].append(x_value)

        # Converting routing logic to VHDL code
        unary_core_code: str = ""
        for segment_idx, core_array in enumerate(unary_core_array):
            for output_value in range(len(core_array)):
                if core_array[output_value][0] != -1:
                    for index, x_value in enumerate(core_array[output_value]):
                        if index == 0:
                            unary_core_code += f"\tcore_{segment_idx}_output({output_value}) <= encoder_output({x_value})"
                        else:
                            unary_core_code += f" or encoder_output({x_value})"
                    unary_core_code += ";\n"
            unary_core_code += "\n"

        # Declaring all core signals
        signals_declaration_code: str = f"\tconstant LARGEST_CORE_VALUE : integer := {largest_core_value};\n\tconstant CORE_OUTPUT_WIDTH : integer := {core_output_width};\n"
        for segment_idx in range(2**ctx.segmentid_width):
            signals_declaration_code += f"\tsignal core_{segment_idx}_output: STD_LOGIC_VECTOR(LARGEST_CORE_VALUE downto 0);\n"

        # Mux for choosing subfunction
        mux_code: str = "\tcore_selector: process(all)\n\tbegin\n\t\tcase to_integer(unsigned(selector)) is\n"
        for i in range(2**ctx.segmentid_width):
            mux_code += f"\t\t\twhen {i} => core_value <= core_{i}_output;\n"
        mux_code += "\t\t\twhen others => core_value <= (others => '0');"
        mux_code += "\n\t\tend case;\n\tend process core_selector;"
        
        # ROM for biases
        rom_code: str = ""
        for segment_idx, bias_value in enumerate(biases):
            rom_code += f"\t\t{segment_idx} => \"{utils.int_to_lsb(bias_value, ctx.data_width)}\",\n"
        rom_code += f"\t\tothers => \"{utils.int_to_lsb(0, ctx.data_width)}\""

        # VHDL complete code generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with ApexHDL
-- Module Name: {ctx.circuit_name}
-- Function: f(x) = {ctx.math_function}
-- Evaluator method: Hybrid
-- Data width: {ctx.data_width} bits
-- Segment index width: {ctx.segmentid_width} bits
-- Range: x in [{ctx.x_min}; {ctx.x_max}[, y in [{ctx.y_min}; {ctx.y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {ctx.circuit_name} is
    generic (
        DATA_WIDTH : positive := {ctx.data_width};
        segmentid_width : positive := {ctx.segmentid_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {ctx.circuit_name};

architecture arch_{ctx.circuit_name} of {ctx.circuit_name} is

    attribute rom_style : string;
    type bias_array_t is array (0 to 2**segmentid_width - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant BIAS_TABLE : bias_array_t := (
{rom_code}
    );
    attribute rom_style of BIAS_TABLE : constant is "distributed";

{signals_declaration_code}
    signal encoder_output: STD_LOGIC_VECTOR(2**(DATA_WIDTH - segmentid_width) - 1 downto 0);
    signal core_value: STD_LOGIC_VECTOR(LARGEST_CORE_VALUE downto 0);
    signal subfunction_value: STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal selector: STD_LOGIC_VECTOR(segmentid_width - 1 downto 0);
    signal bias: STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal least_significants: STD_LOGIC_VECTOR(DATA_WIDTH - segmentid_width - 1 downto 0);

begin

    selector <= input_a(DATA_WIDTH - 1 downto DATA_WIDTH - segmentid_width);
    least_significants <= input_a(DATA_WIDTH - segmentid_width - 1 downto 0);
    bias <= BIAS_TABLE(to_integer(unsigned(selector)));

    -- One-hot encoder    
    one_hot_encoder: process(least_significants)
    begin
        encoder_output <= (others => '0');
        encoder_output(to_integer(unsigned(least_significants))) <= '1';
    end process one_hot_encoder;

    -- Unary cores
{unary_core_code}

    -- Mux
{mux_code}

    -- One-hot decoder
    one_hot_decoder: process(core_value)
    begin
        subfunction_value <= (others => '0');
        for i in 0 to core_value'length - 1 loop
            if core_value(i) = '1' then
                subfunction_value <= std_logic_vector(to_unsigned(i, subfunction_value'length));
            end if;
        end loop;
    end process one_hot_decoder;
    
    adder: process(subfunction_value, bias)
        variable sum : integer := 0;
    begin
        sum := to_integer(unsigned(subfunction_value)) + to_integer(unsigned(bias));
        if sum > 2**DATA_WIDTH - 1 then
            sum := 2**DATA_WIDTH - 1;
        elsif sum < 0 then
            sum := 0;
        end if;
        result <= std_logic_vector(to_unsigned(sum, DATA_WIDTH));
    end process adder;


end arch_{ctx.circuit_name};
        """

        # VHDL file writing
        file_path: Path = folder_path / f"{ctx.circuit_name}.vhd"
        file_path.write_text(vhdl_code)

        return {}