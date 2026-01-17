import paramiko
from scp import SCPClient
import os

# Configuration
PYNQ_IP = "192.168.2.99"
USERNAME = "xilinx"
PASSWORD = "xilinx"

# SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(PYNQ_IP, username=USERNAME, password=PASSWORD)

# Transfer files
with SCPClient(ssh.get_transport()) as scp:
    scp.put("design.bit", "/home/xilinx/sandbox/design.bit")
    scp.put("design.hwh", "/home/xilinx/sandbox/design.hwh")
    scp.put("target.py", "/home/xilinx/sandbox/target.py")


# Single command that does everything
cmd = '''
cd /home/xilinx/sandbox && echo "xilinx" | sudo -S su -c '
source /etc/profile.d/pynq_venv.sh
source /etc/profile.d/xrt_setup.sh
python3 target.py
'
'''

stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=120)

print("Output:")
print(stdout.read().decode())

error = stderr.read().decode()
if error:
    print("Errors:")
    print(error)

remote_image = "/home/xilinx/sandbox/output.png"
local_image = "./fpga_result_local.png"

try:
    
    # Check if file exists
    stdin, stdout, stderr = ssh.exec_command(f'ls -la {remote_image}')
    if stdout.read().decode():
        # Download the image
        scp.get(remote_image, local_image)
        if os.path.exists(local_image):
            file_size = os.path.getsize(local_image)
            print(f"Successfully downloaded {local_image} ({file_size} bytes)")
        else:
            print("Download failed")
    else:
        print(f"Image not found at {remote_image}")
        
except Exception as e:
    print(f"Error: {e}")

finally:
    scp.close()
    ssh.close()
    print("Done!")