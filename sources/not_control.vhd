-------------------------------------
-- Engineer: Florian Delhon
-- Module Name: not_control - behavorial
-- Target: PYNQ-Z2
-- Description: NOT gate
-- Revision: v0.01
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity not_control is
    generic (
        PRECISION : positive := 8
    );
    port (
        input_a : in STD_LOGIC_VECTOR(PRECISION - 1 downto 0);
        result : out STD_LOGIC_VECTOR(PRECISION - 1 downto 0)
    );
end not_control;

architecture behavorial of not_control is
begin
   
    result <= not input_a;

end behavorial;
