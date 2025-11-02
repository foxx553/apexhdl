
-------------------------------------
-- Engineer: Florian Delhon
-- Target: PYNQ-Z2
-- Module Name: unary_8bit_sin
-- Function: f(x) = sin(x*pi)
-- Evaluator method: Unary
-- Data width: 8 bits
-- Range: x in [-1;1[, y in [-1;1[
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity unary_8bit_sin is
    generic (
        DATA_WIDTH : positive := 8
    );
    port (
        input_a : in STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0);
        result : out STD_LOGIC_VECTOR(DATA_WIDTH - 1 downto 0)
    );
end unary_8bit_sin;

architecture arch_unary_8bit_sin of unary_8bit_sin is

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
	decoder_input(0) <= encoder_output(0) xor encoder_output(61);
	decoder_input(1) <= encoder_output(0) xor encoder_output(58) xor encoder_output(68);
	decoder_input(2) <= encoder_output(0) xor encoder_output(56) xor encoder_output(71);
	decoder_input(3) <= encoder_output(0) xor encoder_output(55) xor encoder_output(73);
	decoder_input(4) <= encoder_output(0) xor encoder_output(54) xor encoder_output(74);
	decoder_input(5) <= encoder_output(0) xor encoder_output(53) xor encoder_output(75);
	decoder_input(6) <= encoder_output(0) xor encoder_output(51) xor encoder_output(76);
	decoder_input(7) <= encoder_output(0) xor encoder_output(50) xor encoder_output(78);
	decoder_input(8) <= encoder_output(0) xor encoder_output(50) xor encoder_output(79);
	decoder_input(9) <= encoder_output(0) xor encoder_output(49) xor encoder_output(79);
	decoder_input(10) <= encoder_output(0) xor encoder_output(48) xor encoder_output(80);
	decoder_input(11) <= encoder_output(0) xor encoder_output(47) xor encoder_output(81);
	decoder_input(12) <= encoder_output(0) xor encoder_output(46) xor encoder_output(82);
	decoder_input(13) <= encoder_output(0) xor encoder_output(46) xor encoder_output(83);
	decoder_input(14) <= encoder_output(0) xor encoder_output(45) xor encoder_output(83);
	decoder_input(15) <= encoder_output(0) xor encoder_output(44) xor encoder_output(84);
	decoder_input(16) <= encoder_output(0) xor encoder_output(44) xor encoder_output(85);
	decoder_input(17) <= encoder_output(0) xor encoder_output(43) xor encoder_output(85);
	decoder_input(18) <= encoder_output(0) xor encoder_output(42) xor encoder_output(86);
	decoder_input(19) <= encoder_output(0) xor encoder_output(42) xor encoder_output(87);
	decoder_input(20) <= encoder_output(0) xor encoder_output(41) xor encoder_output(87);
	decoder_input(21) <= encoder_output(0) xor encoder_output(41) xor encoder_output(88);
	decoder_input(22) <= encoder_output(0) xor encoder_output(40) xor encoder_output(88);
	decoder_input(23) <= encoder_output(0) xor encoder_output(39) xor encoder_output(89);
	decoder_input(24) <= encoder_output(0) xor encoder_output(39) xor encoder_output(90);
	decoder_input(25) <= encoder_output(0) xor encoder_output(38) xor encoder_output(90);
	decoder_input(26) <= encoder_output(0) xor encoder_output(38) xor encoder_output(91);
	decoder_input(27) <= encoder_output(0) xor encoder_output(37) xor encoder_output(91);
	decoder_input(28) <= encoder_output(0) xor encoder_output(37) xor encoder_output(92);
	decoder_input(29) <= encoder_output(0) xor encoder_output(36) xor encoder_output(92);
	decoder_input(30) <= encoder_output(0) xor encoder_output(36) xor encoder_output(93);
	decoder_input(31) <= encoder_output(0) xor encoder_output(35) xor encoder_output(93);
	decoder_input(32) <= encoder_output(0) xor encoder_output(35) xor encoder_output(94);
	decoder_input(33) <= encoder_output(0) xor encoder_output(34) xor encoder_output(94);
	decoder_input(34) <= encoder_output(0) xor encoder_output(34) xor encoder_output(95);
	decoder_input(35) <= encoder_output(0) xor encoder_output(33) xor encoder_output(95);
	decoder_input(36) <= encoder_output(0) xor encoder_output(33) xor encoder_output(96);
	decoder_input(37) <= encoder_output(0) xor encoder_output(32) xor encoder_output(96);
	decoder_input(38) <= encoder_output(0) xor encoder_output(32) xor encoder_output(97);
	decoder_input(39) <= encoder_output(0) xor encoder_output(32) xor encoder_output(97);
	decoder_input(40) <= encoder_output(0) xor encoder_output(31) xor encoder_output(97);
	decoder_input(41) <= encoder_output(0) xor encoder_output(31) xor encoder_output(98);
	decoder_input(42) <= encoder_output(0) xor encoder_output(30) xor encoder_output(98);
	decoder_input(43) <= encoder_output(0) xor encoder_output(30) xor encoder_output(99);
	decoder_input(44) <= encoder_output(0) xor encoder_output(29) xor encoder_output(99);
	decoder_input(45) <= encoder_output(0) xor encoder_output(29) xor encoder_output(100);
	decoder_input(46) <= encoder_output(0) xor encoder_output(29) xor encoder_output(100);
	decoder_input(47) <= encoder_output(0) xor encoder_output(28) xor encoder_output(100);
	decoder_input(48) <= encoder_output(0) xor encoder_output(28) xor encoder_output(101);
	decoder_input(49) <= encoder_output(0) xor encoder_output(27) xor encoder_output(101);
	decoder_input(50) <= encoder_output(0) xor encoder_output(27) xor encoder_output(102);
	decoder_input(51) <= encoder_output(0) xor encoder_output(27) xor encoder_output(102);
	decoder_input(52) <= encoder_output(0) xor encoder_output(26) xor encoder_output(102);
	decoder_input(53) <= encoder_output(0) xor encoder_output(26) xor encoder_output(103);
	decoder_input(54) <= encoder_output(0) xor encoder_output(25) xor encoder_output(103);
	decoder_input(55) <= encoder_output(0) xor encoder_output(25) xor encoder_output(104);
	decoder_input(56) <= encoder_output(0) xor encoder_output(25) xor encoder_output(104);
	decoder_input(57) <= encoder_output(0) xor encoder_output(24) xor encoder_output(104);
	decoder_input(58) <= encoder_output(0) xor encoder_output(24) xor encoder_output(105);
	decoder_input(59) <= encoder_output(0) xor encoder_output(24) xor encoder_output(105);
	decoder_input(60) <= encoder_output(0) xor encoder_output(23) xor encoder_output(105);
	decoder_input(61) <= encoder_output(0) xor encoder_output(23) xor encoder_output(106);
	decoder_input(62) <= encoder_output(0) xor encoder_output(22) xor encoder_output(106);
	decoder_input(63) <= encoder_output(0) xor encoder_output(22) xor encoder_output(107);
	decoder_input(64) <= encoder_output(0) xor encoder_output(22) xor encoder_output(107);
	decoder_input(65) <= encoder_output(0) xor encoder_output(21) xor encoder_output(107);
	decoder_input(66) <= encoder_output(0) xor encoder_output(21) xor encoder_output(108);
	decoder_input(67) <= encoder_output(0) xor encoder_output(21) xor encoder_output(108);
	decoder_input(68) <= encoder_output(0) xor encoder_output(20) xor encoder_output(108);
	decoder_input(69) <= encoder_output(0) xor encoder_output(20) xor encoder_output(109);
	decoder_input(70) <= encoder_output(0) xor encoder_output(19) xor encoder_output(109);
	decoder_input(71) <= encoder_output(0) xor encoder_output(19) xor encoder_output(110);
	decoder_input(72) <= encoder_output(0) xor encoder_output(19) xor encoder_output(110);
	decoder_input(73) <= encoder_output(0) xor encoder_output(18) xor encoder_output(110);
	decoder_input(74) <= encoder_output(0) xor encoder_output(18) xor encoder_output(111);
	decoder_input(75) <= encoder_output(0) xor encoder_output(18) xor encoder_output(111);
	decoder_input(76) <= encoder_output(0) xor encoder_output(17) xor encoder_output(111);
	decoder_input(77) <= encoder_output(0) xor encoder_output(17) xor encoder_output(112);
	decoder_input(78) <= encoder_output(0) xor encoder_output(17) xor encoder_output(112);
	decoder_input(79) <= encoder_output(0) xor encoder_output(16) xor encoder_output(112);
	decoder_input(80) <= encoder_output(0) xor encoder_output(16) xor encoder_output(113);
	decoder_input(81) <= encoder_output(0) xor encoder_output(16) xor encoder_output(113);
	decoder_input(82) <= encoder_output(0) xor encoder_output(15) xor encoder_output(113);
	decoder_input(83) <= encoder_output(0) xor encoder_output(15) xor encoder_output(114);
	decoder_input(84) <= encoder_output(0) xor encoder_output(15) xor encoder_output(114);
	decoder_input(85) <= encoder_output(0) xor encoder_output(14) xor encoder_output(114);
	decoder_input(86) <= encoder_output(0) xor encoder_output(14) xor encoder_output(115);
	decoder_input(87) <= encoder_output(0) xor encoder_output(14) xor encoder_output(115);
	decoder_input(88) <= encoder_output(0) xor encoder_output(13) xor encoder_output(115);
	decoder_input(89) <= encoder_output(0) xor encoder_output(13) xor encoder_output(116);
	decoder_input(90) <= encoder_output(0) xor encoder_output(13) xor encoder_output(116);
	decoder_input(91) <= encoder_output(0) xor encoder_output(12) xor encoder_output(116);
	decoder_input(92) <= encoder_output(0) xor encoder_output(12) xor encoder_output(117);
	decoder_input(93) <= encoder_output(0) xor encoder_output(12) xor encoder_output(117);
	decoder_input(94) <= encoder_output(0) xor encoder_output(11) xor encoder_output(117);
	decoder_input(95) <= encoder_output(0) xor encoder_output(11) xor encoder_output(118);
	decoder_input(96) <= encoder_output(0) xor encoder_output(11) xor encoder_output(118);
	decoder_input(97) <= encoder_output(0) xor encoder_output(10) xor encoder_output(118);
	decoder_input(98) <= encoder_output(0) xor encoder_output(10) xor encoder_output(119);
	decoder_input(99) <= encoder_output(0) xor encoder_output(10) xor encoder_output(119);
	decoder_input(100) <= encoder_output(0) xor encoder_output(9) xor encoder_output(119);
	decoder_input(101) <= encoder_output(0) xor encoder_output(9) xor encoder_output(120);
	decoder_input(102) <= encoder_output(0) xor encoder_output(9) xor encoder_output(120);
	decoder_input(103) <= encoder_output(0) xor encoder_output(8) xor encoder_output(120);
	decoder_input(104) <= encoder_output(0) xor encoder_output(8) xor encoder_output(121);
	decoder_input(105) <= encoder_output(0) xor encoder_output(8) xor encoder_output(121);
	decoder_input(106) <= encoder_output(0) xor encoder_output(7) xor encoder_output(121);
	decoder_input(107) <= encoder_output(0) xor encoder_output(7) xor encoder_output(122);
	decoder_input(108) <= encoder_output(0) xor encoder_output(7) xor encoder_output(122);
	decoder_input(109) <= encoder_output(0) xor encoder_output(6) xor encoder_output(122);
	decoder_input(110) <= encoder_output(0) xor encoder_output(6) xor encoder_output(123);
	decoder_input(111) <= encoder_output(0) xor encoder_output(6) xor encoder_output(123);
	decoder_input(112) <= encoder_output(0) xor encoder_output(5) xor encoder_output(123);
	decoder_input(113) <= encoder_output(0) xor encoder_output(5) xor encoder_output(124);
	decoder_input(114) <= encoder_output(0) xor encoder_output(5) xor encoder_output(124);
	decoder_input(115) <= encoder_output(0) xor encoder_output(4) xor encoder_output(124);
	decoder_input(116) <= encoder_output(0) xor encoder_output(4) xor encoder_output(125);
	decoder_input(117) <= encoder_output(0) xor encoder_output(4) xor encoder_output(125);
	decoder_input(118) <= encoder_output(0) xor encoder_output(4) xor encoder_output(125);
	decoder_input(119) <= encoder_output(0) xor encoder_output(3) xor encoder_output(125);
	decoder_input(120) <= encoder_output(0) xor encoder_output(3) xor encoder_output(126);
	decoder_input(121) <= encoder_output(0) xor encoder_output(3) xor encoder_output(126);
	decoder_input(122) <= encoder_output(0) xor encoder_output(2) xor encoder_output(126);
	decoder_input(123) <= encoder_output(0) xor encoder_output(2) xor encoder_output(127);
	decoder_input(124) <= encoder_output(0) xor encoder_output(2) xor encoder_output(127);
	decoder_input(125) <= encoder_output(0) xor encoder_output(1) xor encoder_output(127);
	decoder_input(126) <= encoder_output(0) xor encoder_output(1) xor encoder_output(128);
	decoder_input(127) <= encoder_output(0) xor encoder_output(1) xor encoder_output(128);
	decoder_input(128) <= encoder_output(0) xor encoder_output(128);
	decoder_input(129) <= encoder_output(129);
	decoder_input(130) <= encoder_output(129);
	decoder_input(131) <= encoder_output(129) xor encoder_output(255);
	decoder_input(132) <= encoder_output(130) xor encoder_output(255);
	decoder_input(133) <= encoder_output(130) xor encoder_output(255);
	decoder_input(134) <= encoder_output(130) xor encoder_output(254);
	decoder_input(135) <= encoder_output(131) xor encoder_output(254);
	decoder_input(136) <= encoder_output(131) xor encoder_output(254);
	decoder_input(137) <= encoder_output(131) xor encoder_output(253);
	decoder_input(138) <= encoder_output(132) xor encoder_output(253);
	decoder_input(139) <= encoder_output(132) xor encoder_output(253);
	decoder_input(140) <= encoder_output(132) xor encoder_output(253);
	decoder_input(141) <= encoder_output(132) xor encoder_output(252);
	decoder_input(142) <= encoder_output(133) xor encoder_output(252);
	decoder_input(143) <= encoder_output(133) xor encoder_output(252);
	decoder_input(144) <= encoder_output(133) xor encoder_output(251);
	decoder_input(145) <= encoder_output(134) xor encoder_output(251);
	decoder_input(146) <= encoder_output(134) xor encoder_output(251);
	decoder_input(147) <= encoder_output(134) xor encoder_output(250);
	decoder_input(148) <= encoder_output(135) xor encoder_output(250);
	decoder_input(149) <= encoder_output(135) xor encoder_output(250);
	decoder_input(150) <= encoder_output(135) xor encoder_output(249);
	decoder_input(151) <= encoder_output(136) xor encoder_output(249);
	decoder_input(152) <= encoder_output(136) xor encoder_output(249);
	decoder_input(153) <= encoder_output(136) xor encoder_output(248);
	decoder_input(154) <= encoder_output(137) xor encoder_output(248);
	decoder_input(155) <= encoder_output(137) xor encoder_output(248);
	decoder_input(156) <= encoder_output(137) xor encoder_output(247);
	decoder_input(157) <= encoder_output(138) xor encoder_output(247);
	decoder_input(158) <= encoder_output(138) xor encoder_output(247);
	decoder_input(159) <= encoder_output(138) xor encoder_output(246);
	decoder_input(160) <= encoder_output(139) xor encoder_output(246);
	decoder_input(161) <= encoder_output(139) xor encoder_output(246);
	decoder_input(162) <= encoder_output(139) xor encoder_output(245);
	decoder_input(163) <= encoder_output(140) xor encoder_output(245);
	decoder_input(164) <= encoder_output(140) xor encoder_output(245);
	decoder_input(165) <= encoder_output(140) xor encoder_output(244);
	decoder_input(166) <= encoder_output(141) xor encoder_output(244);
	decoder_input(167) <= encoder_output(141) xor encoder_output(244);
	decoder_input(168) <= encoder_output(141) xor encoder_output(243);
	decoder_input(169) <= encoder_output(142) xor encoder_output(243);
	decoder_input(170) <= encoder_output(142) xor encoder_output(243);
	decoder_input(171) <= encoder_output(142) xor encoder_output(242);
	decoder_input(172) <= encoder_output(143) xor encoder_output(242);
	decoder_input(173) <= encoder_output(143) xor encoder_output(242);
	decoder_input(174) <= encoder_output(143) xor encoder_output(241);
	decoder_input(175) <= encoder_output(144) xor encoder_output(241);
	decoder_input(176) <= encoder_output(144) xor encoder_output(241);
	decoder_input(177) <= encoder_output(144) xor encoder_output(240);
	decoder_input(178) <= encoder_output(145) xor encoder_output(240);
	decoder_input(179) <= encoder_output(145) xor encoder_output(240);
	decoder_input(180) <= encoder_output(145) xor encoder_output(239);
	decoder_input(181) <= encoder_output(146) xor encoder_output(239);
	decoder_input(182) <= encoder_output(146) xor encoder_output(239);
	decoder_input(183) <= encoder_output(146) xor encoder_output(238);
	decoder_input(184) <= encoder_output(147) xor encoder_output(238);
	decoder_input(185) <= encoder_output(147) xor encoder_output(238);
	decoder_input(186) <= encoder_output(147) xor encoder_output(237);
	decoder_input(187) <= encoder_output(148) xor encoder_output(237);
	decoder_input(188) <= encoder_output(148) xor encoder_output(236);
	decoder_input(189) <= encoder_output(149) xor encoder_output(236);
	decoder_input(190) <= encoder_output(149) xor encoder_output(236);
	decoder_input(191) <= encoder_output(149) xor encoder_output(235);
	decoder_input(192) <= encoder_output(150) xor encoder_output(235);
	decoder_input(193) <= encoder_output(150) xor encoder_output(235);
	decoder_input(194) <= encoder_output(150) xor encoder_output(234);
	decoder_input(195) <= encoder_output(151) xor encoder_output(234);
	decoder_input(196) <= encoder_output(151) xor encoder_output(233);
	decoder_input(197) <= encoder_output(152) xor encoder_output(233);
	decoder_input(198) <= encoder_output(152) xor encoder_output(233);
	decoder_input(199) <= encoder_output(152) xor encoder_output(232);
	decoder_input(200) <= encoder_output(153) xor encoder_output(232);
	decoder_input(201) <= encoder_output(153) xor encoder_output(232);
	decoder_input(202) <= encoder_output(153) xor encoder_output(231);
	decoder_input(203) <= encoder_output(154) xor encoder_output(231);
	decoder_input(204) <= encoder_output(154) xor encoder_output(230);
	decoder_input(205) <= encoder_output(155) xor encoder_output(230);
	decoder_input(206) <= encoder_output(155) xor encoder_output(230);
	decoder_input(207) <= encoder_output(155) xor encoder_output(229);
	decoder_input(208) <= encoder_output(156) xor encoder_output(229);
	decoder_input(209) <= encoder_output(156) xor encoder_output(228);
	decoder_input(210) <= encoder_output(157) xor encoder_output(228);
	decoder_input(211) <= encoder_output(157) xor encoder_output(228);
	decoder_input(212) <= encoder_output(157) xor encoder_output(227);
	decoder_input(213) <= encoder_output(158) xor encoder_output(227);
	decoder_input(214) <= encoder_output(158) xor encoder_output(226);
	decoder_input(215) <= encoder_output(159) xor encoder_output(226);
	decoder_input(216) <= encoder_output(159) xor encoder_output(225);
	decoder_input(217) <= encoder_output(160) xor encoder_output(225);
	decoder_input(218) <= encoder_output(160) xor encoder_output(225);
	decoder_input(219) <= encoder_output(160) xor encoder_output(224);
	decoder_input(220) <= encoder_output(161) xor encoder_output(224);
	decoder_input(221) <= encoder_output(161) xor encoder_output(223);
	decoder_input(222) <= encoder_output(162) xor encoder_output(223);
	decoder_input(223) <= encoder_output(162) xor encoder_output(222);
	decoder_input(224) <= encoder_output(163) xor encoder_output(222);
	decoder_input(225) <= encoder_output(163) xor encoder_output(221);
	decoder_input(226) <= encoder_output(164) xor encoder_output(221);
	decoder_input(227) <= encoder_output(164) xor encoder_output(220);
	decoder_input(228) <= encoder_output(165) xor encoder_output(220);
	decoder_input(229) <= encoder_output(165) xor encoder_output(219);
	decoder_input(230) <= encoder_output(166) xor encoder_output(219);
	decoder_input(231) <= encoder_output(166) xor encoder_output(218);
	decoder_input(232) <= encoder_output(167) xor encoder_output(218);
	decoder_input(233) <= encoder_output(167) xor encoder_output(217);
	decoder_input(234) <= encoder_output(168) xor encoder_output(216);
	decoder_input(235) <= encoder_output(169) xor encoder_output(216);
	decoder_input(236) <= encoder_output(169) xor encoder_output(215);
	decoder_input(237) <= encoder_output(170) xor encoder_output(215);
	decoder_input(238) <= encoder_output(170) xor encoder_output(214);
	decoder_input(239) <= encoder_output(171) xor encoder_output(213);
	decoder_input(240) <= encoder_output(172) xor encoder_output(213);
	decoder_input(241) <= encoder_output(172) xor encoder_output(212);
	decoder_input(242) <= encoder_output(173) xor encoder_output(211);
	decoder_input(243) <= encoder_output(174) xor encoder_output(211);
	decoder_input(244) <= encoder_output(174) xor encoder_output(210);
	decoder_input(245) <= encoder_output(175) xor encoder_output(209);
	decoder_input(246) <= encoder_output(176) xor encoder_output(208);
	decoder_input(247) <= encoder_output(177) xor encoder_output(207);
	decoder_input(248) <= encoder_output(178) xor encoder_output(207);
	decoder_input(249) <= encoder_output(178) xor encoder_output(206);
	decoder_input(250) <= encoder_output(179) xor encoder_output(204);
	decoder_input(251) <= encoder_output(181) xor encoder_output(203);
	decoder_input(252) <= encoder_output(182) xor encoder_output(202);
	decoder_input(253) <= encoder_output(183) xor encoder_output(201);
	decoder_input(254) <= encoder_output(184) xor encoder_output(199);
	decoder_input(255) <= encoder_output(186);


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


end arch_unary_8bit_sin;
    