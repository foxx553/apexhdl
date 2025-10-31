from utils import compute_discrete_output, int_to_lsb

def rom_method(args):
    """ Generate VHDL code for a ROM function evaluator """

    # Args check
    if len(args) != 7:
        print("Usage: generate_evaluator.py rom <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>")
        return
    
    # Args extraction
    evaluator_name = args[0]
    function_of_x = args[1]
    data_width, x_min, x_max, y_min, y_max = map(int, args[2:7])

    # Discrete output calculation
    y_discrete_values = compute_discrete_output(function_of_x, data_width, x_min, x_max, y_min, y_max)

    # VHDL behavioral code generation
    rom_code = ""
    for x_value, y_value in enumerate(y_discrete_values):
        rom_code += f"\t\t{x_value} => \"{int_to_lsb(y_value, data_width)}\",\n"
    rom_code += f"\t\tothers => \"{int_to_lsb(0, data_width)}\""

    # VHDL complete code generation
    return f"""
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: {evaluator_name}
-- Function: f(x) = {function_of_x}
-- Evaluator method: ROM
-- Data width: {data_width} bits
-- Range: x in [{x_min};{x_max}[, y in [{y_min};{y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {evaluator_name} is
    generic (
        DATA_WIDTH : positive := {data_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {evaluator_name};

architecture arch_{evaluator_name} of {evaluator_name} is
    
    attribute rom_style : string;
    type rom_array_t is array (0 to 2**DATA_WIDTH - 1) of STD_LOGIC_VECTOR (DATA_WIDTH - 1 downto 0);
    constant ROM_VALUES : rom_array_t := (
{rom_code}
    );
    attribute rom_style of ROM_VALUES : constant is "distributed";

begin

    result <= ROM_VALUES(to_integer(unsigned(input_a)));

end arch_{evaluator_name};
    """

def binary_method(args):
    """ Generate VHDL code for a binary function evaluator """

    return ""

def unary_method(args):
    """ Generate VHDL code for a unary function evaluator """

    # Args check
    if len(args) != 7:
        print("Usage: generate_evaluator.py unary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max>")
        return
    
    # Args extraction
    evaluator_name = args[0]
    function_of_x = args[1]
    data_width, x_min, x_max, y_min, y_max = map(int, args[2:7])

    # Discrete output calculation
    y_discrete_values = compute_discrete_output(function_of_x, data_width, x_min, x_max, y_min, y_max)

    # Computing unary core routing logic
    unary_core_array = [[-1] for _ in range(2**data_width)]
    for output_value in range(2**data_width):
        for x_value, y_value in enumerate(y_discrete_values):
            if y_value == output_value:
                if unary_core_array[output_value][0] == -1:
                    unary_core_array[output_value][0] = x_value
                else:
                    unary_core_array[output_value].append(x_value)
    
    # Converting routing logic to VHDL code
    unary_core_code = ""
    for output_value in range(len(unary_core_array)):
        if unary_core_array[output_value][0] != -1:
            for index, x_value in enumerate(unary_core_array[output_value]):
                if index == 0:
                    unary_core_code += f"\tdecoder_input({output_value}) <= encoder_output({x_value})"
                else:
                    unary_core_code += f" or encoder_output({x_value})"
            unary_core_code += ";\n"

    # VHDL complete code generation
    return f"""
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: {evaluator_name}
-- Function: f(x) = {function_of_x}
-- Evaluator method: Unary
-- Data width: {data_width} bits
-- Range: x in [{x_min};{x_max}[, y in [{y_min};{y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {evaluator_name} is
    generic (
        DATA_WIDTH : positive := {data_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {evaluator_name};

architecture arch_{evaluator_name} of {evaluator_name} is

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

end arch_{evaluator_name};
    """

def hybrid_method(args):
    """ Generate VHDL code for a hybrid binary/unary function evaluator """

    return ""

evaluation_methods_map = {
    "rom": rom_method,
    "binary": binary_method,
    "unary": unary_method,
    "hybrid": hybrid_method
}   