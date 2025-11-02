from utils import compute_discrete_output, int_to_lsb, parse_function

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
    y_discrete_values = compute_discrete_output(function_of_x, data_width, x_min, x_max, data_width, y_min, y_max)

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
    type rom_array_t is array (0 to 2**DATA_WIDTH - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
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

    # Args check
    if len(args) != 9:
        print("Usage: generate_evaluator.py binary <evaluator_name> <function_of_x> <data_width> <x_min> <x_max> <y_min> <y_max> <segment_idx_width> <group_idx_width>")
        return
    
    # Args extraction
    evaluator_name = args[0]
    function_of_x = args[1]
    data_width, x_min, x_max, y_min, y_max, segment_idx_width, group_idx_width = map(int, args[2:9])
    segment_width = data_width - segment_idx_width

    # Offset table calculation
    function_calculator = parse_function(function_of_x)
    offset_table = []
    delta_x_group = (x_max - x_min) / 2**group_idx_width
    delta_x_segment = (x_max - x_min) / 2**segment_idx_width
    for i in range(2**group_idx_width):
        group_slope = (function_calculator((i + 1) * delta_x_group) - function_calculator(i * delta_x_group)) / delta_x_group
        offset_table += compute_discrete_output(f"{group_slope}*x", segment_width, 0, delta_x_segment, data_width, 0, y_max - y_min)

    # Input table calculation
    input_table = compute_discrete_output(function_of_x, segment_idx_width, x_min, x_max, data_width, y_min, y_max)

    # VHDL behavioral code generation
    offset_code = ""
    for x_value, y_value in enumerate(offset_table):
        offset_code += f"\t\t{x_value} => \"{int_to_lsb(y_value, data_width)}\",\n"
    offset_code += f"\t\tothers => \"{int_to_lsb(0, data_width)}\""
    input_code = ""
    for x_value, y_value in enumerate(input_table):
        input_code += f"\t\t{x_value} => \"{int_to_lsb(y_value, data_width)}\",\n"
    input_code += f"\t\tothers => \"{int_to_lsb(0, data_width)}\""

    # VHDL complete code generation
    return f"""
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: {evaluator_name}
-- Function: f(x) = {function_of_x}
-- Evaluator method: Binary
-- Data width: {data_width} bits
-- Group index width: {group_idx_width} bits
-- Segment index width: {segment_idx_width} bits
-- Range: x in [{x_min};{x_max}[, y in [{y_min};{y_max}[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity {evaluator_name} is
    generic (
        DATA_WIDTH : positive := {data_width};
        GROUP_IDX_WIDTH : positive := {group_idx_width};
        SEGMENT_IDX_WIDTH : positive := {segment_idx_width}
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end {evaluator_name};

architecture arch_{evaluator_name} of {evaluator_name} is
    
    attribute rom_style : string;
    signal offset_entry : STD_LOGIC_VECTOR(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH - 1 downto 0);
    signal offset_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal input_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    
    -- Offset table
    type offset_array_t is array (0 to 2**(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH) - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
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

    offset_entry <= input_a(DATA_WIDTH - 1 downto DATA_WIDTH - GROUP_IDX_WIDTH) & input_a(DATA_WIDTH - SEGMENT_IDX_WIDTH - 1 downto 0);

    offset_value <= OFFSET_TABLE(to_integer(unsigned(offset_entry)));

    input_value <= INPUT_TABLE(to_integer(unsigned(input_a(DATA_WIDTH - 1 downto DATA_WIDTH - SEGMENT_IDX_WIDTH))));

    adder: process(input_value, offset_value)
        variable sum : integer := 0;
    begin
        sum := to_integer(unsigned(offset_value)) + to_integer(unsigned(input_value));
        if sum > 2**DATA_WIDTH - 1 then
            sum := 2**DATA_WIDTH - 1;
        end if;
        result <= std_logic_vector(to_unsigned(sum, DATA_WIDTH));
    end process adder;

end arch_{evaluator_name};
    """

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
    y_discrete_values = compute_discrete_output(function_of_x, data_width, x_min, x_max, data_width, y_min, y_max)

    # Computing unary core routing logic
    unary_core_array = [[0 for _ in range(2**data_width)] for _ in range(2**data_width)]
    y_cursor = 0
    unary_core_array[0][0] = 1
    for x_value, y_value in enumerate(y_discrete_values):
        if y_value != y_cursor:
            step = 1 if y_value > y_cursor else -1
            for i in range(y_cursor + step, y_value + step, step):
                unary_core_array[i][x_value] = 1
            y_cursor = y_value

    # Converting routing logic to VHDL code
    unary_core_code = ""
    for y_value, x_values in enumerate(unary_core_array):
        has_one = False
        for x_value, is_connected in enumerate(x_values):
            if is_connected == 1:
                if not has_one:
                    unary_core_code += f"\tdecoder_input({y_value}) <= encoder_output({x_value})"
                    has_one = True
                else:
                    unary_core_code += f" xor encoder_output({x_value})"
        if has_one:
            unary_core_code += f";\n"

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

    -- Thermometer encoder
    thermometer_encoder: process(input_a)
        variable input_int : integer;
    begin
        input_int := to_integer(unsigned(input_a));
        for i in 0 to 2**DATA_WIDTH - 1 loop
            if i <= input_int then
                encoder_output(i) <= '1';
            else
                encoder_output(i) <= '0';
            end if;
        end loop;
    end process thermometer_encoder;


    -- Unary core
{unary_core_code}

    -- Thermometer decoder
    thermometer_decoder: process(decoder_input)
        variable count : integer := 0;
    begin
        count := 0;
        for i in 1 to 2**DATA_WIDTH - 1 loop
            if decoder_input(i) = '1' then
                count := count + 1;
            end if;
        end loop;
        result <= std_logic_vector(to_unsigned(count, DATA_WIDTH));
    end process thermometer_decoder;


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