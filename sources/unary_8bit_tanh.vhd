
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: unary_8bit_tanh
-- Function: f(x) = (1+tanh(4*(2*x-1)))/2
-- Evaluator method: Unary
-- Data width: 8 bits
-- Range: x in [0;1[, y in [0;1[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity unary_8bit_tanh is
    generic (
        DATA_WIDTH : positive := 8
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end unary_8bit_tanh;

architecture arch_unary_8bit_tanh of unary_8bit_tanh is

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
	decoder_input(0) <= encoder_output(0) or encoder_output(1) or encoder_output(2) or encoder_output(3) or encoder_output(4) or encoder_output(5) or encoder_output(6) or encoder_output(7) or encoder_output(8) or encoder_output(9) or encoder_output(10) or encoder_output(11) or encoder_output(12) or encoder_output(13) or encoder_output(14) or encoder_output(15) or encoder_output(16) or encoder_output(17) or encoder_output(18) or encoder_output(19) or encoder_output(20) or encoder_output(21) or encoder_output(22) or encoder_output(23) or encoder_output(24) or encoder_output(25) or encoder_output(26) or encoder_output(27) or encoder_output(28);
	decoder_input(1) <= encoder_output(29) or encoder_output(30) or encoder_output(31) or encoder_output(32) or encoder_output(33) or encoder_output(34) or encoder_output(35) or encoder_output(36) or encoder_output(37) or encoder_output(38) or encoder_output(39) or encoder_output(40) or encoder_output(41) or encoder_output(42) or encoder_output(43) or encoder_output(44) or encoder_output(45);
	decoder_input(2) <= encoder_output(46) or encoder_output(47) or encoder_output(48) or encoder_output(49) or encoder_output(50) or encoder_output(51) or encoder_output(52) or encoder_output(53) or encoder_output(54);
	decoder_input(3) <= encoder_output(55) or encoder_output(56) or encoder_output(57) or encoder_output(58) or encoder_output(59);
	decoder_input(4) <= encoder_output(60) or encoder_output(61) or encoder_output(62) or encoder_output(63);
	decoder_input(5) <= encoder_output(64) or encoder_output(65) or encoder_output(66);
	decoder_input(6) <= encoder_output(67) or encoder_output(68) or encoder_output(69);
	decoder_input(7) <= encoder_output(70) or encoder_output(71);
	decoder_input(8) <= encoder_output(72) or encoder_output(73) or encoder_output(74);
	decoder_input(9) <= encoder_output(75);
	decoder_input(10) <= encoder_output(76) or encoder_output(77);
	decoder_input(11) <= encoder_output(78) or encoder_output(79);
	decoder_input(12) <= encoder_output(80);
	decoder_input(13) <= encoder_output(81);
	decoder_input(14) <= encoder_output(82);
	decoder_input(15) <= encoder_output(83) or encoder_output(84);
	decoder_input(16) <= encoder_output(85);
	decoder_input(17) <= encoder_output(86);
	decoder_input(18) <= encoder_output(87);
	decoder_input(19) <= encoder_output(88);
	decoder_input(21) <= encoder_output(89);
	decoder_input(22) <= encoder_output(90);
	decoder_input(23) <= encoder_output(91);
	decoder_input(24) <= encoder_output(92);
	decoder_input(26) <= encoder_output(93);
	decoder_input(27) <= encoder_output(94);
	decoder_input(29) <= encoder_output(95);
	decoder_input(31) <= encoder_output(96);
	decoder_input(32) <= encoder_output(97);
	decoder_input(34) <= encoder_output(98);
	decoder_input(36) <= encoder_output(99);
	decoder_input(38) <= encoder_output(100);
	decoder_input(40) <= encoder_output(101);
	decoder_input(42) <= encoder_output(102);
	decoder_input(44) <= encoder_output(103);
	decoder_input(47) <= encoder_output(104);
	decoder_input(49) <= encoder_output(105);
	decoder_input(52) <= encoder_output(106);
	decoder_input(54) <= encoder_output(107);
	decoder_input(57) <= encoder_output(108);
	decoder_input(60) <= encoder_output(109);
	decoder_input(63) <= encoder_output(110);
	decoder_input(66) <= encoder_output(111);
	decoder_input(69) <= encoder_output(112);
	decoder_input(72) <= encoder_output(113);
	decoder_input(75) <= encoder_output(114);
	decoder_input(79) <= encoder_output(115);
	decoder_input(82) <= encoder_output(116);
	decoder_input(86) <= encoder_output(117);
	decoder_input(89) <= encoder_output(118);
	decoder_input(93) <= encoder_output(119);
	decoder_input(97) <= encoder_output(120);
	decoder_input(100) <= encoder_output(121);
	decoder_input(104) <= encoder_output(122);
	decoder_input(108) <= encoder_output(123);
	decoder_input(112) <= encoder_output(124);
	decoder_input(116) <= encoder_output(125);
	decoder_input(120) <= encoder_output(126);
	decoder_input(124) <= encoder_output(127);
	decoder_input(128) <= encoder_output(128);
	decoder_input(132) <= encoder_output(129);
	decoder_input(136) <= encoder_output(130);
	decoder_input(140) <= encoder_output(131);
	decoder_input(144) <= encoder_output(132);
	decoder_input(148) <= encoder_output(133);
	decoder_input(152) <= encoder_output(134);
	decoder_input(156) <= encoder_output(135);
	decoder_input(159) <= encoder_output(136);
	decoder_input(163) <= encoder_output(137);
	decoder_input(167) <= encoder_output(138);
	decoder_input(170) <= encoder_output(139);
	decoder_input(174) <= encoder_output(140);
	decoder_input(177) <= encoder_output(141);
	decoder_input(181) <= encoder_output(142);
	decoder_input(184) <= encoder_output(143);
	decoder_input(187) <= encoder_output(144);
	decoder_input(190) <= encoder_output(145);
	decoder_input(193) <= encoder_output(146);
	decoder_input(196) <= encoder_output(147);
	decoder_input(199) <= encoder_output(148);
	decoder_input(202) <= encoder_output(149);
	decoder_input(204) <= encoder_output(150);
	decoder_input(207) <= encoder_output(151);
	decoder_input(209) <= encoder_output(152);
	decoder_input(212) <= encoder_output(153);
	decoder_input(214) <= encoder_output(154);
	decoder_input(216) <= encoder_output(155);
	decoder_input(218) <= encoder_output(156);
	decoder_input(220) <= encoder_output(157);
	decoder_input(222) <= encoder_output(158);
	decoder_input(224) <= encoder_output(159);
	decoder_input(225) <= encoder_output(160);
	decoder_input(227) <= encoder_output(161);
	decoder_input(229) <= encoder_output(162);
	decoder_input(230) <= encoder_output(163);
	decoder_input(232) <= encoder_output(164);
	decoder_input(233) <= encoder_output(165);
	decoder_input(234) <= encoder_output(166);
	decoder_input(235) <= encoder_output(167);
	decoder_input(237) <= encoder_output(168);
	decoder_input(238) <= encoder_output(169);
	decoder_input(239) <= encoder_output(170);
	decoder_input(240) <= encoder_output(171);
	decoder_input(241) <= encoder_output(172) or encoder_output(173);
	decoder_input(242) <= encoder_output(174);
	decoder_input(243) <= encoder_output(175);
	decoder_input(244) <= encoder_output(176);
	decoder_input(245) <= encoder_output(177) or encoder_output(178);
	decoder_input(246) <= encoder_output(179) or encoder_output(180);
	decoder_input(247) <= encoder_output(181);
	decoder_input(248) <= encoder_output(182) or encoder_output(183) or encoder_output(184);
	decoder_input(249) <= encoder_output(185) or encoder_output(186);
	decoder_input(250) <= encoder_output(187) or encoder_output(188) or encoder_output(189);
	decoder_input(251) <= encoder_output(190) or encoder_output(191) or encoder_output(192);
	decoder_input(252) <= encoder_output(193) or encoder_output(194) or encoder_output(195) or encoder_output(196);
	decoder_input(253) <= encoder_output(197) or encoder_output(198) or encoder_output(199) or encoder_output(200) or encoder_output(201);
	decoder_input(254) <= encoder_output(202) or encoder_output(203) or encoder_output(204) or encoder_output(205) or encoder_output(206) or encoder_output(207) or encoder_output(208) or encoder_output(209) or encoder_output(210);
	decoder_input(255) <= encoder_output(211) or encoder_output(212) or encoder_output(213) or encoder_output(214) or encoder_output(215) or encoder_output(216) or encoder_output(217) or encoder_output(218) or encoder_output(219) or encoder_output(220) or encoder_output(221) or encoder_output(222) or encoder_output(223) or encoder_output(224) or encoder_output(225) or encoder_output(226) or encoder_output(227) or encoder_output(228) or encoder_output(229) or encoder_output(230) or encoder_output(231) or encoder_output(232) or encoder_output(233) or encoder_output(234) or encoder_output(235) or encoder_output(236) or encoder_output(237) or encoder_output(238) or encoder_output(239) or encoder_output(240) or encoder_output(241) or encoder_output(242) or encoder_output(243) or encoder_output(244) or encoder_output(245) or encoder_output(246) or encoder_output(247) or encoder_output(248) or encoder_output(249) or encoder_output(250) or encoder_output(251) or encoder_output(252) or encoder_output(253) or encoder_output(254) or encoder_output(255);


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

end arch_unary_8bit_tanh;
    