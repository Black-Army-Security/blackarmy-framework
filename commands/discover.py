import os
import subprocess

def run_and_log_command(command, output_file):
    """Run a command, log its output to a file, and display it on the screen."""
    try:
        with open(output_file, "a") as f:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Read and process stdout
            for line in process.stdout:
                decoded_line = line.decode("utf-8")
                print(decoded_line, end="")  # Print to the screen
                f.write(decoded_line)  # Write to the file

            # Read and process stderr
            for line in process.stderr:
                decoded_line = line.decode("utf-8")
                if decoded_line.strip():  # Only log non-empty lines
                    print(decoded_line, end="")  # Print to the screen
                    f.write(decoded_line)  # Write to the file
    except Exception as e:
        print(f"Error executing command: {e}")

def discover(domain, wordlist):
    if not domain or not wordlist:
        print("Error: Missing arguments for 'discover'. Usage: discover domain.com -w /path/to/wordlist.txt")
        return

    if not os.path.isfile(wordlist):
        print(f"Error: Wordlist file '{wordlist}' not found.")
        return

    output_file = f"/var/tmp/{domain}.txt"
    subdomain_enum = f"gobuster dns -d {domain} -w {wordlist} -v > /var/tmp/raw_output.txt"
    dns_regs_enum = f"amass enum -d {domain}"

    print(f"Running Subdomain enumeration for domain: {domain}")
    os.system(subdomain_enum)

    try:
        with open("/var/tmp/raw_output.txt", "r") as raw_output:
            subdomains = []
            for line in raw_output:
                if "Found:" in line:
                    subdomain = line.split("Found:")[1].strip()
                    subdomains.append(subdomain)
                    print(f"Discovered subdomain: {subdomain}")

        os.remove("/var/tmp/raw_output.txt")

        with open(output_file, "a") as final_output:
            for subdomain in subdomains:
                nslookup_command = f"nslookup -debug {subdomain} > /var/tmp/nslookup_output.txt"
                os.system(nslookup_command)

                try:
                    with open("/var/tmp/nslookup_output.txt", "r") as nslookup_output:
                        in_non_auth_section = False
                        ips = []
                        for line in nslookup_output:
                            if "Non-authoritative answer:" in line:
                                in_non_auth_section = True
                            elif in_non_auth_section and "Address:" in line:
                                ip = line.split("Address:")[1].strip()
                                ips.append(ip)
                            elif in_non_auth_section and line == "\n":
                                break

                    os.remove("/var/tmp/nslookup_output.txt")

                    final_output.write(subdomain)
                    if ips:
                        final_output.write("  " + ", ".join(ips))
                    final_output.write("\n")

                except FileNotFoundError:
                    print(f"Error: Could not open nslookup output file for {subdomain}")
                    continue

        print(f"DNS enumeration and IP resolution completed. Results saved to {output_file}")

        # Run amass enumeration and log output
        print(f"Running DNS enumeration for domain: {domain}")
        run_and_log_command(f"{dns_regs_enum} >> {output_file}", output_file)

    except FileNotFoundError:
        print("Error: Could not open raw output file.")