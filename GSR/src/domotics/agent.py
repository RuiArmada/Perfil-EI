import socket
import time
import threading
import os
import signal
import sys
from datetime import datetime, timedelta
from colorama import init, Fore
from mib_loader import recursive_store_data, json_data  # Import json_data from mib_loader
from data_store import store_data, retrieve_data, store_error
from pdu import create_pdu, parse_pdu, get_timestamp
import netifaces as ni
from security import generate_keys, ensure_keys_exist, load_private_key, load_public_key, encrypt_message, decrypt_message

# Initialize colorama
init(autoreset=True)

# Agent configurations
AGENT_IP = '127.0.0.1'
AGENT_PORT = 5000
BUFFER_SIZE = 1024
DISCOVERY_PORT = 7000
DISCOVERY_RESPONSE = "Agent_Response"
TIMEOUT = 5  # Timeout for discovery in seconds

# Key paths
AGENT_PRIVATE_KEY_PATH = "../agent_private_key.pem"
AGENT_PUBLIC_KEY_PATH = "../agent_public_key.pem"
MANAGER_PUBLIC_KEY_PATH = "../manager_public_key.pem"

# Ensure keys exist
ensure_keys_exist(AGENT_PRIVATE_KEY_PATH, AGENT_PUBLIC_KEY_PATH)

# Load keys
try:
    agent_private_key = load_private_key(AGENT_PRIVATE_KEY_PATH)
    agent_public_key = load_public_key(AGENT_PUBLIC_KEY_PATH)
except Exception as e:
    print(f"{Fore.RED}Error loading keys: {e}")
    sys.exit(1)

# Ensure manager public key exists, generate a temporary pair if not (for testing purposes)
if not os.path.exists(MANAGER_PUBLIC_KEY_PATH):
    generate_keys("temp_manager_private_key.pem", MANAGER_PUBLIC_KEY_PATH)

try:
    manager_public_key = load_public_key(MANAGER_PUBLIC_KEY_PATH)
except Exception as e:
    print(f"{Fore.RED}Error loading manager public key: {e}")
    sys.exit(1)

# Load and initialize data store
try:
    recursive_store_data("", json_data)
except Exception as e:
    print(f"{Fore.RED}Error initializing data store: {e}")
    sys.exit(1)

def get_broadcast_address():
    try:
        interfaces = ni.interfaces()
        for interface in interfaces:
            addrs = ni.ifaddresses(interface)
            if ni.AF_INET in addrs:
                for addr in addrs[ni.AF_INET]:
                    if 'broadcast' in addr:
                        return addr['broadcast']
    except Exception as e:
        print(f"{Fore.RED}Error getting broadcast address: {e}")
    return None

BROADCAST_ADDRESS = get_broadcast_address() or '<broadcast>'

def handle_get_request(iid_list):
    values = []
    print("\n")
    for iid in iid_list.split(','):
        value = retrieve_data(iid)
        print(f"{Fore.YELLOW}Retrieving IID {iid}: {value}")  # Debugging
        if value is not None:
            values.append(str(value))
        else:
            values.append("Unknown IID")
    return values

def handle_set_request(device_id, iid_list, value_list):
    iids = iid_list.split(',')
    values = value_list.split(',')
    error_occurred = False
    for iid, value in zip(iids, values):
        full_iid = f"{device_id}.{iid}"
        if full_iid in json_data and json_data[full_iid].get("ACCESS") == "read-only":
            print(f"{Fore.RED}Attempt to modify read-only IID: {full_iid}")
            store_error(f"Attempt to modify read-only IID: {full_iid}")
            error_occurred = True
        elif not store_data(full_iid, value):
            store_error(f"Unknown IID: {full_iid}")
            error_occurred = True
    return error_occurred

def graceful_exit(signum, frame):
    print(f"{Fore.RED}Gracefully shutting down the agent...")
    sys.exit(0)

# Register signal handlers for graceful exit
signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

# Create UDP socket
try:
    agent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    agent_socket.bind((AGENT_IP, AGENT_PORT))
except socket.error as e:
    print(f"{Fore.RED}Socket error: {e}")
    sys.exit(1)

print(f"{Fore.GREEN}Agent is running...")

# Uptime updater function
def update_uptime():
    while True:
        try:
            for key, value in json_data.items():
                if "upTime" in key:
                    current_uptime = retrieve_data(key)
                    if current_uptime:
                        time_parts = list(map(int, current_uptime.split(":")))
                        current_time = timedelta(days=time_parts[0], hours=time_parts[1], minutes=time_parts[2], seconds=time_parts[3], milliseconds=time_parts[4])
                        new_time = current_time + timedelta(seconds=1)
                        new_uptime = f"{new_time.days}:{new_time.seconds//3600}:{(new_time.seconds//60)%60}:{new_time.seconds%60}:{new_time.microseconds//1000}"
                        store_data(key, new_uptime)
        except Exception as e:
            print(f"{Fore.RED}Error updating uptime: {e}")
        time.sleep(1)

# Start uptime updater thread
uptime_thread = threading.Thread(target=update_uptime)
uptime_thread.daemon = True
uptime_thread.start()

while True:
    try:
        data, addr = agent_socket.recvfrom(BUFFER_SIZE)
    except socket.error as e:
        print(f"{Fore.RED}Error receiving data: {e}")
        continue
    
    decrypted_data = decrypt_message(data.decode(), agent_private_key)
    print(f"\n{Fore.BLUE}Received message from {addr}: {decrypted_data}")
    
    if decrypted_data is None:
        print(f"{Fore.RED}Decryption failed or received invalid data.")
        continue
    
    try:
        pdu = parse_pdu(decrypted_data)
    except Exception as e:
        print(f"{Fore.RED}Error parsing PDU: {e}")
        continue

    if pdu["tag"] != "kdk847ufh84jg87g":
        response_pdu = create_pdu("kdk847ufh84jg87g", "R", pdu["message_identifier"], "", "", "2")
        encrypted_response_pdu = encrypt_message(response_pdu, manager_public_key)
        if encrypted_response_pdu:
            agent_socket.sendto(encrypted_response_pdu.encode(), addr)
        print(f"\n{Fore.MAGENTA}Sent response to {addr}: {response_pdu}\n")
        continue

    error_occurred = False
    if pdu["type"] == "G":
        values = handle_get_request(pdu["iids"])
        response_pdu = create_pdu("kdk847ufh84jg87g", "R", pdu["message_identifier"], pdu["iids"], ','.join(values), "0")
    elif pdu["type"] == "S":
        device_id = pdu["iids"].split('.')[0]
        error_occurred = handle_set_request(device_id, '.'.join(pdu["iids"].split('.')[1:]), pdu["values"])
        error_code = "1" if error_occurred else "0"
        response_pdu = create_pdu("kdk847ufh84jg87g", "R", pdu["message_identifier"], "", "", error_code)
    elif pdu["type"] == "D":
        response_pdu = create_pdu("kdk847ufh84jg87g", "R", pdu["message_identifier"], "", "", "0")
    else:
        response_pdu = create_pdu("kdk847ufh84jg87g", "R", pdu["message_identifier"], "", "", "3")

    encrypted_response_pdu = encrypt_message(response_pdu, manager_public_key)
    if encrypted_response_pdu:
        agent_socket.sendto(encrypted_response_pdu.encode(), addr)
    print(f"\n{Fore.MAGENTA}Sent response to {addr}: {response_pdu}\n")
