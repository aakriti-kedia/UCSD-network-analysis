import csv
import re

def extract_ping_data(line):
    ping_pattern_1 = r'Pinging (\S+) \[(\d+\.\d+\.\d+\.\d+)\] with \d+ bytes of data'
    ping_pattern_2 = r'\.+PING (\S+) \((\d+\.\d+\.\d+\.\d+)\): \d+ data bytes'
    
    match_1 = re.search(ping_pattern_1, line)
    match_2 = re.search(ping_pattern_2, line)
    
    if match_1:
        domain = match_1.group(1)
        ip_address = match_1.group(2)
        return domain, ip_address
    elif match_2:
        domain = match_2.group(1)
        ip_address = match_2.group(2)
        return domain, ip_address
    return None, None

def extract_icmp_data(line):
    icmp_pattern_1 = r'Reply from (\d+\.\d+\.\d+\.\d+): bytes=\d+ time=([\d.]+)ms TTL=(\d+)'
    icmp_pattern_2 = r'\d+ bytes from (\d+\.\d+\.\d+\.\d+): icmp_seq=\d+ ttl=(\d+) time=([\d.]+) ms'
    
    match_1 = re.search(icmp_pattern_1, line)
    match_2 = re.search(icmp_pattern_2, line)
    
    if match_1:
        ip_address = match_1.group(1)
        ttl = match_1.group(3)
        time = match_1.group(2)
        return ip_address, ttl, time
    elif match_2:
        ip_address = match_2.group(1)
        ttl = match_2.group(2)
        time = match_2.group(3)
        return ip_address, ttl, time
    return None, None, None

def process_file(file_path):
    print("Processing ", file_path)
    ip_to_domain = {}
    output_rows = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            domain, ip_address = extract_ping_data(line)
            if domain and ip_address:
                ip_to_domain[ip_address] = domain

            ip_address, ttl, time = extract_icmp_data(line)
            if ip_address and ttl and time:
                if ip_address in ip_to_domain:
                    output_rows.append([ip_to_domain[ip_address], ip_address, time, ttl])
                else:
                    output_rows.append(['Unknown', ip_address, time, ttl])

    return output_rows

def write_to_csv(out_filepath, output_rows, date, log_name, from_ip, write_mode):
    headers = ['Date', 'From', 'From IP', 'To',	'To_IP', 'Ping Time', 'TTL']

    file_mode = 'w' if write_mode else 'a'

    with open(out_filepath, file_mode, newline='') as file:
        writer = csv.writer(file)
        if write_mode:
            writer.writerow(headers)
        for row in output_rows:
            writer.writerow([date, log_name, from_ip, *row])

""" 
logs - List of Tuples of format (date, log_name, from_ip) 
write_mode - Boolean. If true, it will erase output_filepath and rewrite it. Else just append it
output_filepath - name of output file
"""
def main(logs, write_mode, output_filepath):
    initial_mode = write_mode # so that write mode is on only for first file
    for (date, log_name, from_ip) in logs:
        file_path = f"logs/{log_name}.log"
        output_rows = process_file(file_path)
        if len(output_rows) == 0:
            print(f"WARNING: No csv rows found from {file_path}")
        write_to_csv(output_filepath, output_rows, date, log_name, from_ip, initial_mode)
        initial_mode = False

if __name__ == "__main__":
    LOGS = [
        ('5/30/2023', 'aman-near-ralphs', '70.95.167.232'),
        ('5/26/2023', 'sanidli-ak', 'Unknown'),
        ('5/26/2023', 'sanidli-aman', 'Unknown'),
        ('Unknown', 'cupertino', 'Unknown'),
        ('5/26/2023', 'downtown-cafe', 'Unknown'),
        ('5/26/2023', 'downtown-verizon', 'Unknown'),
        ('5/26/2023', 'downtown', 'Unknown'),
        ('Unknown', 'eduroam-cse', 'Unknown'),
        ('Unknown', 'geisel', 'Unknown'),
        ('Unknown', 'home-akhil', 'Unknown'),
        ('5/26/2023', 'la-jolla', 'Unknown'),
        ('5/26/2023', 'miramar', 'Unknown'),
        ('Unknown', 'san-airport', 'Unknown'),
    ]
    OUTPUT_FILEPATH = "logs/output.csv"
    main(LOGS, True, OUTPUT_FILEPATH)