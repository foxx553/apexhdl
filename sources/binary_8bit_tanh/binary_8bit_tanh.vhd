
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: binary_8bit_tanh
-- Function: f(x) = (1+tanh(4*(2*x-1)))/2
-- Evaluator method: Binary
-- Data width: 8 bits
-- Group index width: 2 bits
-- Segment index width: 4 bits
-- Range: x in [0;1[, y in [0;1[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity binary_8bit_tanh is
    generic (
        DATA_WIDTH : positive := 8;
        GROUP_IDX_WIDTH : positive := 2;
        SEGMENT_IDX_WIDTH : positive := 4
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end binary_8bit_tanh;

architecture arch_binary_8bit_tanh of binary_8bit_tanh is
    
    attribute rom_style : string;
    signal offset_entry : STD_LOGIC_VECTOR(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH - 1 downto 0);
    signal offset_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal input_value : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    
    -- Offset table
    type offset_array_t is array (0 to 2**(GROUP_IDX_WIDTH + DATA_WIDTH - SEGMENT_IDX_WIDTH) - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant OFFSET_TABLE : offset_array_t := (
		0 => "00000000",
		1 => "00000000",
		2 => "00000000",
		3 => "00000000",
		4 => "00000000",
		5 => "00000000",
		6 => "00000000",
		7 => "00000000",
		8 => "00000001",
		9 => "00000001",
		10 => "00000001",
		11 => "00000001",
		12 => "00000001",
		13 => "00000001",
		14 => "00000001",
		15 => "00000001",
		16 => "00000000",
		17 => "00000010",
		18 => "00000100",
		19 => "00000110",
		20 => "00001000",
		21 => "00001010",
		22 => "00001100",
		23 => "00001101",
		24 => "00001111",
		25 => "00010001",
		26 => "00010011",
		27 => "00010101",
		28 => "00010111",
		29 => "00011001",
		30 => "00011011",
		31 => "00011101",
		32 => "00000000",
		33 => "00000010",
		34 => "00000100",
		35 => "00000110",
		36 => "00001000",
		37 => "00001010",
		38 => "00001100",
		39 => "00001101",
		40 => "00001111",
		41 => "00010001",
		42 => "00010011",
		43 => "00010101",
		44 => "00010111",
		45 => "00011001",
		46 => "00011011",
		47 => "00011101",
		48 => "00000000",
		49 => "00000000",
		50 => "00000000",
		51 => "00000000",
		52 => "00000000",
		53 => "00000000",
		54 => "00000000",
		55 => "00000000",
		56 => "00000001",
		57 => "00000001",
		58 => "00000001",
		59 => "00000001",
		60 => "00000001",
		61 => "00000001",
		62 => "00000001",
		63 => "00000001",
		others => "00000000"
    );
    attribute rom_style of OFFSET_TABLE : constant is "distributed";

    -- Input table
    type input_array_t is array (0 to 2**SEGMENT_IDX_WIDTH - 1) of STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    constant INPUT_TABLE : input_array_t := (
		0 => "00000000",
		1 => "00000000",
		2 => "00000001",
		3 => "00000010",
		4 => "00000101",
		5 => "00001100",
		6 => "00011111",
		7 => "01000101",
		8 => "10000000",
		9 => "10111011",
		10 => "11100001",
		11 => "11110100",
		12 => "11111011",
		13 => "11111110",
		14 => "11111111",
		15 => "11111111",
		others => "00000000"
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

end arch_binary_8bit_tanh;
    