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

def process_file(file_path, encoding_type):
    print("Processing ", file_path)
    ip_to_domain = {}
    output_rows = []

    with open(file_path, 'r', encoding=encoding_type) as file:
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
    for (label, date, log_name, from_ip, encoding_type) in logs:
        file_path = f"more-logs/{log_name}"
        output_rows = process_file(file_path, encoding_type)
        if len(output_rows) == 0:
            print(f"WARNING: No csv rows found from {file_path}")
        print(f"INFO: {len(output_rows)} loaded for label {label}")
        write_to_csv(output_filepath, output_rows, date, label, from_ip, initial_mode)
        initial_mode = False

if __name__ == "__main__":
    # LOGS = [
    #     ('5/30/2023', 'aman-near-ralphs', '70.95.167.232'),
    #     ('5/26/2023', 'sanidli-ak', 'Unknown'),
    #     ('5/26/2023', 'sanidli-aman', 'Unknown'),
    #     ('Unknown', 'cupertino', 'Unknown'),
    #     ('5/26/2023', 'downtown-cafe', 'Unknown'),
    #     ('5/26/2023', 'downtown-verizon', 'Unknown'),
    #     ('5/26/2023', 'downtown', 'Unknown'),
    #     ('Unknown', 'eduroam-cse', 'Unknown'),
    #     ('Unknown', 'geisel', 'Unknown'),
    #     ('Unknown', 'home-akhil', 'Unknown'),
    #     ('5/26/2023', 'la-jolla', 'Unknown'),
    #     ('5/26/2023', 'miramar', 'Unknown'),
    #     ('Unknown', 'san-airport', 'Unknown'),
    # ]
    LOGS = [
        # ('ping_CB', '6/3/2023', 'ping 107.77.227.186 - 2', "Unknown (IP of mobile hotspot)"),
        # ('ping_CA', '6/3/2023', 'ping ieng6.ucsd.edu - 2', "Unknown (IP of mobile hotspot)"),
        ('ping_BC', '8/3/2023', 'ieng6_ucsd_wifi.txt', 'Unknown (IP of UCSD wifi)', 'utf-8'),
        ('ping_AC', '7/3/2023', 'full-route.txt',  "Unknown (IP of mobile hotspot)", 'utf-16'),
        # ('ping_AC', '7/3/2023', 'full-route2.txt',  "Unknown (IP of mobile hotspot)", 'utf-16'),
        ('ping_AB', '7/3/2023', 'mobile-att-log.txt',  "Unknown (IP of mobile hotspot)", 'utf-16'),
        # ('ping_AB', '7/3/2023', 'mobile-att-log2.txt',  "Unknown (IP of mobile hotspot)", 'utf-16'),
    ]
    OUTPUT_FILEPATH = "more-logs/latest-output.csv"
    main(LOGS, True, OUTPUT_FILEPATH)