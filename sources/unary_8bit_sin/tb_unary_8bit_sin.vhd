
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: tb_unary_8bit_sin
-- Description: Testbench for module unary_8bit_sin
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use STD.TEXTIO.ALL;

entity tb_unary_8bit_sin is
end tb_unary_8bit_sin;

architecture arch_tb_unary_8bit_sin of tb_unary_8bit_sin is

    constant DATA_WIDTH : positive := 8;

    signal input_a : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
    signal result  : STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);

    component unary_8bit_sin
        generic (
            DATA_WIDTH : positive := 8
        );
        port (
            input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
            result  : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
        );
    end component;

    file output_file : TEXT open WRITE_MODE is "../sources/unary_8bit_sin/results_unary_8bit_sin.txt";

begin

    uut: unary_8bit_sin
        generic map (
            DATA_WIDTH => DATA_WIDTH
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

end arch_tb_unary_8bit_sin;
