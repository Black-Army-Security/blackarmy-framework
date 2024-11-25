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
   

