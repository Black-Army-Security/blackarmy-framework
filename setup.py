import subprocess
import os
import sys

# Check if the script is run with administrative privileges
if os.geteuid() != 0:
    print("""
[ERROR] Permission Denied!
This script requires administrative privileges to run.

Please re-run the script using sudo:
    sudo python3 setup.py

If you believe this is an error, ensure you have the correct permissions.
""")
    sys.exit(1)

# Path to save configuration files
main_path = '/usr/share/blackarmy-framework'
config_path = '/usr/share/blackarmy-framework/config'
scan_dir_path = '/usr/share/blackarmy-framework/scans/'
discover_scans_path = '/usr/share/blackarmy-framework/scans/discover_scans/'
webdiscover_scans_path = '/usr/share/blackarmy-framework/scans/webdiscover_scans/'

blackdb_file = 'blackdb.py'

# Tools to be checked
tools = ["gobuster", "amass", "nmap", "nslookup", "wafw00f", "nikto", "dirb"]

# Line to be checked in the /etc/apt/sources.list file
kali_repo = "deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware"
sourcelist_file = "/etc/apt/sources.list"



# Function to check if a tool is installed
def check_tool(tool):
    try:
        subprocess.run(["which", tool], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to add the line to /etc/apt/sources.list, if necessary
def check_sourcelist():
    try:
        with open(sourcelist_file, "r") as file:
            content = file.read()
        if kali_repo not in content:
            with open(sourcelist_file, "a") as file:
                file.write(f"\n{kali_repo}\n")
            print(f"Line added to {sourcelist_file}: {kali_repo}")
            return True
    except PermissionError:
        print("Permission denied. Run the script as root to modify /etc/apt/sources.list.")
        return False
    return True

# Function to install missing tools
def install_tools(missing_tools):
    if missing_tools:
        try:
            print("Updating package list...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            print(f"Installing tools: {', '.join(missing_tools)}")
            subprocess.run(["sudo", "apt-get", "install", "-y"] + missing_tools, check=True)
            print("Tools successfully installed.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing tools: {e}")
    else:
        print("All tools are already installed.")




# Check if the main directory exists
if not os.path.exists(main_path):    
    os.mkdir(main_path)    
    print(f"Directory '{main_path}' created successfully.")


# Check if the config directory exists    
if not os.path.exists(config_path):
    os.mkdir(config_path)
    print(f"Directory '{config_path}' created successfully.")

# Check if the scan directory exists    
if not os.path.exists(scan_dir_path):
    os.mkdir(scan_dir_path)
    print(f"Directory '{scan_dir_path}' created successfully.")
   

if not os.path.exists(discover_scans_path):
    os.mkdir(discover_scans_path)
    print(f"Directory '{discover_scans_path}' created successfully.")
   

if not os.path.exists(webdiscover_scans_path):
    os.mkdir(webdiscover_scans_path)
    print(f"Directory '{webdiscover_scans_path}' created successfully.")


try:
    print("Setting up the database...")
    subprocess.run(["sudo", "python3", blackdb_file], check=True)
    print("Database setup completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error during setup: {e.stderr}")
   
# Check tools and install missing ones
missing_tools = [tool for tool in tools if not check_tool(tool)]
if missing_tools:
    print(f"Missing tools: {', '.join(missing_tools)}")
    if check_sourcelist():
        install_tools(missing_tools)
else:
    print("All tools are installed.")