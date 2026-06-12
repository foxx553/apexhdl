from pathlib import Path
import subprocess
import shutil
import zipfile
from string import Template
import paramiko
from paramiko import SSHClient, Transport
from scp import SCPClient # type: ignore

from apex.context import Context
from apex.implementation_stage.implementation_registry import ImplementationRegistry, ImplementationStage
import apex.utils as utils

@ImplementationRegistry.register(predicate=lambda ctx: ctx.step == "impl" and ctx.synthesis_tool == "vivado" and ctx.fpga_board == "xc7z020clg400-1", priority=1)
class ImplementationPynq(ImplementationStage):
    """
    PYNQ implementation stage
    """
    
    def execute(self, ctx: Context) -> dict[str, float]:

        # Preliminary checks
        if ctx.fpga_board is None or ctx.ip_address is None or ctx.username is None or ctx.password is None:
            raise ValueError("PYNQ implementation requires fpga_board, ip_address, username and password to be set")

        # Get source folder path
        folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "vhdl"

        # Get TCL script path
        tcl_script: Path = Path("../tcl/implement_evaluator.tcl")

        # Create impl folder
        impl_folder_path: Path = ctx.output_folder_path / ctx.circuit_name / "impl"
        impl_folder_path.mkdir(parents=True, exist_ok=True)

        # AXI-Stream top file generation
        vhdl_code: str = f"""
-------------------------------------
-- Generated with ApexHDL
-- Target: {ctx.fpga_board}
-- Module Name: stream_top_{ctx.circuit_name}
-- Description: AXI-Stream top module for circuit {ctx.circuit_name}
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

        # Vivado logs target path
        log_file: Path = impl_folder_path / "vivado.log"

        # Vivado execution in batch mode
        cmd: str = f"vivado -mode batch -source {tcl_script} -log {log_file} -tclargs {ctx.fpga_board} {ctx.output_folder_path} {ctx.circuit_name}"
        subprocess.run(cmd, shell=True, text=True)
        
        # Removing old logs and putting in new Vivado logs
        Path(impl_folder_path / "vivado.log").unlink(missing_ok=True)
        shutil.move("vivado.log", impl_folder_path)

        # Extracting HWH from XSA archive
        xsa_archive: Path = impl_folder_path / f"{ctx.circuit_name}.xsa"
        with zipfile.ZipFile(xsa_archive, 'r') as xsa_zip:
            hwh_internal_name: str = next(f for f in xsa_zip.namelist() if f.endswith('.hwh'))
            extracted_path: Path = Path(xsa_zip.extract(hwh_internal_name, impl_folder_path))
            extracted_path.replace(impl_folder_path / f"{ctx.circuit_name}.hwh")
        xsa_archive.unlink(missing_ok=True)

        # Generating target Python code from template
        template_file: Path = Path("./apex/implementation_stage/variants/res/target.py.tmpl")
        target_file: Path = impl_folder_path / "target.py"
        template: Template = Template(template_file.read_text())
        target_script: str = template.substitute(module_name=ctx.circuit_name, data_width=ctx.data_width)
        target_file.write_text(target_script)

        # Establishing SSH connection to the board
        ssh: SSHClient = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ctx.ip_address, username=ctx.username, password=ctx.password)
        transport: Transport | None = ssh.get_transport()
        if transport is None:
            raise RuntimeError("Failed to establish SSH transport")

        # Transferring files with SCP
        with SCPClient(transport) as scp:
            scp.put(f"{str(impl_folder_path)}/{ctx.circuit_name}.bit", f"{ctx.fpga_working_folder_path}/{ctx.circuit_name}.bit")
            scp.put(f"{str(impl_folder_path)}/{ctx.circuit_name}.hwh", f"{ctx.fpga_working_folder_path}/{ctx.circuit_name}.hwh")
            scp.put(f"{str(impl_folder_path)}/target.py", f"{ctx.fpga_working_folder_path}/target.py")
        
        # Command for target script execution (needs PYNQ setup via specific bash scripts)
        pynq_cmd: str = f'''
cd {ctx.fpga_working_folder_path} && echo "xilinx" | sudo -S su -c '
source /etc/profile.d/pynq_venv.sh
source /etc/profile.d/xrt_setup.sh
python3 target.py
'
        '''
        ssh.exec_command(pynq_cmd, get_pty=True) 
            
        # Downloading output files with SCP
        scp.get(f"{ctx.fpga_working_folder_path}/outputs_{ctx.circuit_name}.csv", f"{str(impl_folder_path)}/outputs_{ctx.circuit_name}.csv")
        
        # Closing connection 
        scp.close()
        ssh.close()

        # Perform outputs results processing
        mean_absolute_error, max_absolute_error, mean_relative_error, max_relative_error = utils.process_outputs_file(
            impl_folder_path / f"outputs_{ctx.circuit_name}.csv",
            impl_folder_path,
            ctx.circuit_name,
            utils.lambdify_function(ctx.math_function),
            ctx.data_width,
            ctx.x_min,
            ctx.x_max,
            ctx.y_min,
            ctx.y_max,
            is_simulation=False
        )

        return {
            "ImplMaxAbsError": max_absolute_error,
            "ImplMeanAbsError": mean_absolute_error,
            "ImplMaxRelError": max_relative_error,
            "ImplMeanRelError": mean_relative_error
        }