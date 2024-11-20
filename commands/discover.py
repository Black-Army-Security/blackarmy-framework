import os
import subprocess

def discover(domain, wordlist):
    output_file = f"/var/tmp/{domain}.txt"
    command = f"gobuster dns -d {domain} -w {wordlist} > /var/tmp/raw_output.txt"

    print(f"Running DNS enum: {command}")
    os.system(command)

    try:
        with open("/var/tmp/raw_output.txt", "r") as raw_output:
            subdomains = []
            for line in raw_output:
                if "Found:" in line:
                    subdomain = line.split("Found:")[1].strip()
                    subdomains.append(subdomain)
                    print(f"Discovered subdomain: {subdomain}")

        os.remove("/var/tmp/raw_output.txt")

        with open(output_file, "w") as final_output:
            for subdomain in subdomains:
                nslookup_command = f"nslookup {subdomain} > /var/tmp/nslookup_output.txt"
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

        print(f"DNS enumeration and IP resolution complete. Results saved to {output_file}")

    except FileNotFoundError:
        print("Error: Could not open raw output file.")
