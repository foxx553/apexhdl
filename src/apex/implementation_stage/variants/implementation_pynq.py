from pathlib import Path
import subprocess
from subprocess import CompletedProcess
import shutil
import zipfile
from string import Template
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from typing import Any

from apex.context import Context
from apex.implementation_stage.implementation_registry import ImplementationRegistry
from apex.implementation_stage.implementation_base import ImplementationStage

@ImplementationRegistry.register(predicate=lambda ctx: ctx.step == "impl" and ctx.implementation_tool == "vivado" and ctx.fpga_board == "xc7z020clg400-1", priority=1)
class ImplementationPynq(ImplementationStage):
    """
    PYNQ implementation stage
    """
    
    def execute(self, ctx: Context) -> bool:

        # Get source folder path
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"

        # Get TCL script path
        tcl_script: Path = Path("../tcl/implement_evaluator.tcl")

        # Create bit folder
        bit_folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "bit"
        bit_folder_path.mkdir(parents=True, exist_ok=True)

        # AXI-Stream top file generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with ApexHDL
-- Target: {ctx.fpga_board}
-- Module Name: stream_top_{ctx.circuit_name}
-- Description: AXI-Stream top module for {ctx.circuit_name}
-------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity stream_top_{ctx.circuit_name} is
    port (
        din_tdata 	: in STD_LOGIC_VECTOR(15 downto 0);
        din_tlast 	: in STD_LOGIC;
        din_tvalid 	: in STD_LOGIC;
        din_tready 	: out STD_LOGIC;
        dout_tdata 	: out STD_LOGIC_VECTOR(15 downto 0);
        dout_tlast 	: out STD_LOGIC;
        dout_tvalid	: out STD_LOGIC;
        dout_tready : in STD_LOGIC;
		clk 		: in STD_LOGIC;
		rstn		: in STD_LOGIC
    );
end stream_top_{ctx.circuit_name};

architecture arch_stream_top_{ctx.circuit_name} of stream_top_{ctx.circuit_name} is

	signal reg_tdata_in 	: STD_LOGIC_VECTOR({ctx.data_width - 1} downto 0);
	signal reg_tvalid_out 	: STD_LOGIC;
	signal reg_en 			: STD_LOGIC;

begin

    uut : entity work.{ctx.circuit_name}
        port map (
            input_a => din_tdata({ctx.data_width - 1} downto 0),
            result  => reg_tdata_in
        );

	reg_tdata : process(clk, rstn)
	begin
		if rstn = '0' then
			dout_tdata <= (others => '0');
		elsif rising_edge(clk) then
			if reg_en = '1' then
				dout_tdata <= (others => '0');
				dout_tdata({ctx.data_width - 1} downto 0) <= reg_tdata_in;
			end if;
		end if;
	end process reg_tdata; 

	reg_tlast : process(clk, rstn)
	begin
		if rstn = '0' then
			dout_tlast <= '0';
		elsif rising_edge(clk) then
			if reg_en = '1' then
				dout_tlast <= din_tlast;
			end if;
		end if;
	end process reg_tlast;

	reg_tvalid : process(clk, rstn)
	begin
		if rstn = '0' then
			reg_tvalid_out <= '0';
		elsif rising_edge(clk) then
			if reg_en = '1' then
				reg_tvalid_out <= din_tvalid;
			end if;
		end if;
	end process reg_tvalid; 

	dout_tvalid <= reg_tvalid_out;
	reg_en <= dout_tready or not reg_tvalid_out;
	din_tready <= reg_en;
	
end arch_stream_top_{ctx.circuit_name};
        """

        # VHDL file writing
        stream_top_file: Path = folder_path / f"stream_top_{ctx.circuit_name}.vhd"
        stream_top_file.write_text(vhdl_code)

        # Vivado execution in batch mode
        cmd = [
            "vivado",
            "-mode", "batch",
            "-source", tcl_script,
            "-tclargs", ctx.output_folder_path, ctx.circuit_name
        ]
        
        # Error handling
        try:
            subprocess.run(cmd, timeout=1800, shell=True, text=True)
        except subprocess.TimeoutExpired:
            print(f"[ERROR] Vivado implementation unsuccessful for circuit {ctx.circuit_name}: 1800 seconds timeout")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Vivado implementation unsuccessful for circuit {ctx.circuit_name}: {e}")
            return False
        
        # Removing old logs and putting in new Vivado logs
        Path(bit_folder_path / "vivado.log").unlink(missing_ok=True)
        shutil.move("vivado.log", bit_folder_path)

        # Extracting HWH from XSA archive
        xsa_archive: Path = bit_folder_path / f"{ctx.circuit_name}.xsa"
        with zipfile.ZipFile(xsa_archive, 'r') as xsa_zip:
            hwh_internal_name: str = next(f for f in xsa_zip.namelist() if f.endswith('.hwh'))
            extracted_path: Path = Path(xsa_zip.extract(hwh_internal_name, bit_folder_path))
            extracted_path.replace(bit_folder_path / f"{ctx.circuit_name}.hwh")
        xsa_archive.unlink(missing_ok=True)

        # Generating target Python code from template
        template_file: Path = Path("../res/target.py.tmpl")
        target_file: Path = bit_folder_path / "target.py"
        template: Template = Template(template_file.read_text())
        target_script: str = template.substitute(
            module_name=ctx.circuit_name,
            function_str=ctx.math_function,
            data_width=ctx.data_width,
            x_min=ctx.x_min,
            x_max=ctx.x_max,
            y_min=ctx.y_min,
            y_max=ctx.y_max
        )
        target_file.write_text(target_script)

        # Establishing SSH connection to the board
        ssh: SSHClient = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ctx.ip_address, username=ctx.username, password=ctx.password)

        # Transferring files with SCP
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(f"{str(bit_folder_path)}/{ctx.circuit_name}.bit", f"{ctx.fpga_working_folder_path}/{ctx.circuit_name}.bit")
            scp.put(f"{str(bit_folder_path)}/{ctx.circuit_name}.hwh", f"{ctx.fpga_working_folder_path}/{ctx.circuit_name}.hwh")
            scp.put(f"{str(bit_folder_path)}/target.py", f"{ctx.fpga_working_folder_path}/target.py")
        
        # Command for target script execution (needs PYNQ setup via specific bash scripts)
        cmd: str = f'''
cd {ctx.fpga_working_folder_path} && echo "xilinx" | sudo -S su -c '
source /etc/profile.d/pynq_venv.sh
source /etc/profile.d/xrt_setup.sh
python3 target.py
'
        '''
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=120)
        exit_status: int = stdout.channel.recv_exit_status() 

        if exit_status == 0:  
            
            # Downloading output files with SCP
            scp.get(f"{ctx.fpga_working_folder_path}/curves_{ctx.circuit_name}.png", f"{str(bit_folder_path)}/curves_{ctx.circuit_name}.png")
            scp.get(f"{ctx.fpga_working_folder_path}/error_absolute_{ctx.circuit_name}.png", f"{str(bit_folder_path)}/error_absolute_{ctx.circuit_name}.png")
            scp.get(f"{ctx.fpga_working_folder_path}/error_relative_{ctx.circuit_name}.png", f"{str(bit_folder_path)}/error_relative_{ctx.circuit_name}.png")
            
            # Closing connection 
            scp.close()
            ssh.close()
            return True
        
        else:
            
            # Error handling and closing connection
            print(f"[ERROR] Target script execution unsuccessful for circuit {ctx.circuit_name}: {stderr.read().decode()}")
            scp.close()
            ssh.close()
            return False