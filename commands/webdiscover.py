import os
import subprocess
from database import connection, crud, models

# Initialize the database
db = connection.Session()

def webdiscover(target_url, wordlist):
    if not target_url or not wordlist:
        print("Error: Missing arguments for 'discover'. Usage: discover target_url.com -w /path/to/wordlist.txt")
        return

    if not os.path.isfile(wordlist):
        print(f"Error: Wordlist file '{wordlist}' not found.")
        return

    # Sanitize target_url to create safe filenames
    safe_target = target_url.replace("://", "_").replace("/", "_")

    # Ensure the /var/tmp directory exists
    output_dir = '/var/tmp'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create output files
    waf_output_file = f'{output_dir}/waf_{safe_target}_output.txt'
    robots_output_file = f'{output_dir}/robots_{safe_target}_output.txt'
    webscan_output_file = f'{output_dir}/webscan_{safe_target}_output.txt'
    dirbruteforce_output_file = f'{output_dir}/dirbruteforce_{safe_target}_output.txt'

    # Commands
    waf_enum = f'wafw00f {target_url} > {waf_output_file}'
    robots_enum = f'gobuster dir -u {target_url} -w robots.txt > {robots_output_file}'
    webscan_enum = f'nikto -h {target_url} > {webscan_output_file}'
    dir_brute_enum = f'dirb {target_url} {wordlist} > {dirbruteforce_output_file}'

    print(f'Running WAF enum on: {target_url}')
    os.system(waf_enum)
    print(f'The WAF scan has finished. Results saved in: {waf_output_file}')
    print(f'Running Robots.txt enum on: {target_url}')
    os.system(robots_enum)
    print(f'The Robots.txt scan has finished. Results saved in: {robots_output_file}')
    print(f'Running Web scan on: {target_url}')
    os.system(webscan_enum)
    print(f'The Web scan has finished. Results saved in: {webscan_output_file}')
    print(f'Running Directory Brute Force on: {target_url}')
    os.system(dir_brute_enum)
    print(f'The Directory Brute Force scan has finished. Results saved in: {dirbruteforce_output_file}')
