
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: tb_binary_8bit_tanh
-- Description: Testbench for module binary_8bit_tanh
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_binary_8bit_tanh is
end tb_binary_8bit_tanh;

architecture arch_tb_binary_8bit_tanh of tb_binary_8bit_tanh is

    constant DATA_WIDTH : positive := 8;
	constant GROUP_IDX_WIDTH : positive := 2;
	constant SEGMENT_IDX_WIDTH : positive := 4;

    signal input_a : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal result  : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);

    component binary_8bit_tanh
        generic (
            DATA_WIDTH : positive := 8;
			GROUP_IDX_WIDTH : positive := 2;
			SEGMENT_IDX_WIDTH : positive := 4
        );
        port (
            input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
            result  : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
        );
    end component;

    file output_file : TEXT open WRITE_MODE is "../sources/binary_8bit_tanh/results_binary_8bit_tanh.txt";

begin

    uut: binary_8bit_tanh
        generic map (
            DATA_WIDTH => DATA_WIDTH,
			GROUP_IDX_WIDTH => GROUP_IDX_WIDTH,
			SEGMENT_IDX_WIDTH => SEGMENT_IDX_WIDTH
        )
        port map (
            input_a => input_a,
            result  => result
        );

    tb_proc: process
        variable line_out : line;
        variable input_str, result_str : string(1 to DATA_WIDTH);
    begin
        for i in 0 to 2**DATA_WIDTH - 1 loop
            input_a <= std_logic_vector(to_unsigned(i, DATA_WIDTH));

            wait for 10 ns;

            write(line_out, integer'image(i));
            write(line_out, string'(","));
            write(line_out, integer'image(to_integer(unsigned(result))));
            writeline(output_file, line_out);

        end loop;
        
        std.env.stop(0);
    end process;

end arch_tb_binary_8bit_tanh;
