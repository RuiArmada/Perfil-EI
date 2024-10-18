import socket
import random
import sys
import os
from time import time, sleep
from pdu import create_pdu, parse_pdu, get_timestamp
from mib_loader import json_data
from colorama import init, Fore
from security import generate_keys, ensure_keys_exist, load_private_key, load_public_key, encrypt_message, decrypt_message

# Initialize colorama
init(autoreset=True)

# Manager configurations
MANAGER_IP = '127.0.0.1'
MANAGER_PORT = 6000
AGENT_IP = '127.0.0.1'
AGENT_PORT = 5000
BUFFER_SIZE = 1024

# Key paths
MANAGER_PRIVATE_KEY_PATH = "../manager_private_key.pem"
MANAGER_PUBLIC_KEY_PATH = "../manager_public_key.pem"
AGENT_PUBLIC_KEY_PATH = "../agent_public_key.pem"

# Ensure keys exist
ensure_keys_exist(MANAGER_PRIVATE_KEY_PATH, MANAGER_PUBLIC_KEY_PATH)

# Load keys
manager_private_key = load_private_key(MANAGER_PRIVATE_KEY_PATH)
manager_public_key = load_public_key(MANAGER_PUBLIC_KEY_PATH)

# Ensure agent public key exists, generate a temporary pair if not (for testing purposes)
if not os.path.exists(AGENT_PUBLIC_KEY_PATH):
    generate_keys("temp_agent_private_key.pem", AGENT_PUBLIC_KEY_PATH)

agent_public_key = load_public_key(AGENT_PUBLIC_KEY_PATH)

# Create UDP socket
manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
manager_socket.bind((MANAGER_IP, MANAGER_PORT))

# Global variable to control detailed response display
show_detailed_response = True

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_error_message(error_code):
    error_messages = {
        "0": "No error",
        "1": "Attempt to modify read-only IID",
        "2": "Invalid tag in PDU",
        "3": "Unknown error"
    }
    return error_messages.get(error_code, "Unknown error")

def send_message(message_type, device_id, iids="", values=""):
    message_type = message_type.upper()  # Ensure the type is uppercase
    message_identifier = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    prefixed_iids = ','.join([f"{device_id}.{iid}" for iid in iids.split(',')])
    pdu = create_pdu("kdk847ufh84jg87g", message_type, message_identifier, prefixed_iids, values, "")
    encrypted_pdu = encrypt_message(pdu, agent_public_key)
    manager_socket.sendto(encrypted_pdu.encode(), (AGENT_IP, AGENT_PORT))
    data, addr = manager_socket.recvfrom(BUFFER_SIZE)
    decrypted_data = decrypt_message(data.decode(), manager_private_key)
    if decrypted_data:
        response = parse_pdu(decrypted_data)
        error_message = get_error_message(response['errors'])
        
        if response['errors'] == '1':  # Error: Attempt to modify read-only IID
            print(f"{Fore.RED}Error: {error_message}")
            return
        
        if show_detailed_response:
            print(f"\n{Fore.GREEN}Received response from {addr}:\n"
                  f"Tag: {response['tag']}\n"
                  f"Type: {response['type']}\n"
                  f"Timestamp: {response['timestamp']}\n"
                  f"Message Identifier: {response['message_identifier']}\n"
                  f"IIDs: {response['iids']}\n"
                  f"Values: {response['values']}\n"
                  f"Errors: {response['errors']}\n")

            # Print IIDs and Values in a more readable format
            if response['iids'] and response['values'] and response['type'] == 'R':
                iids_list = response['iids'].split(',')
                values_list = response['values'].split(',')
                print(f"\n{Fore.BLUE}Device Information:")
                for iid, value in zip(iids_list, values_list):
                    print(f"{Fore.YELLOW}{iid}: {Fore.WHITE}{value}")
            
            # Check for other errors and display user-friendly message
            if response['errors'] != '0':
                print(f"{Fore.RED}Error: {error_message}")
        else:
            if message_type == 'G' and response['values']:
                print(f"\n{Fore.GREEN}Operation successful.\n")
                iids_list = response['iids'].split(',')
                values_list = response['values'].split(',')
                for iid, value in zip(iids_list, values_list):
                    print(f"{Fore.YELLOW}{iid}: {Fore.WHITE}{value}")
            else:
                print(f"\n{Fore.GREEN}Operation successful.\n")

    else:
        print(f"{Fore.RED}Failed to decrypt the message")

def send_discovery_pdu():
    message_identifier = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    pdu = create_pdu("kdk847ufh84jg87g", "D", message_identifier, "", "", "")
    encrypted_pdu = encrypt_message(pdu, agent_public_key)
    manager_socket.sendto(encrypted_pdu.encode(), (AGENT_IP, AGENT_PORT))
    print(f"\n{Fore.MAGENTA}Sent discovery message: {pdu}\n")
    
    agents = []
    start_time = time()
    
    while time() - start_time < 5:
        manager_socket.settimeout(5 - (time() - start_time))
        try:
            data, addr = manager_socket.recvfrom(BUFFER_SIZE)
            decrypted_data = decrypt_message(data.decode(), manager_private_key)
            if decrypted_data:
                response = parse_pdu(decrypted_data)
                if response["type"] == "R" and response["errors"] == "0":
                    agents.append(addr)
        except socket.timeout:
            break

    return agents

def query_device_status(device_id):
    iids = ",".join([
        "id", "type", "beaconRate", 
        "nSensors", "nActuators", "dateAndTime", 
        "upTime", "lastTimeUpdated", "operationalStatus", 
        "reset"
    ])
    send_message('G', device_id, iids)

def extract_device_ids(mib_data):
    return [key for key in mib_data.keys() if key.startswith('device') and '.' not in key]

def show_tutorial():
    clear_screen()
    print(f"{Fore.CYAN}MIB Structure Schematic:\n"
          f"{Fore.CYAN}-----------------------------------------\n"
          f"{Fore.CYAN}| MIB                                    |\n"
          f"{Fore.CYAN}|  |-- device (Group)                    |\n"
          f"{Fore.CYAN}|  |    |-- id (String)                  |\n"
          f"{Fore.CYAN}|  |    |-- type (String)                |\n"
          f"{Fore.CYAN}|  |    |-- beaconRate (Integer)         |\n"
          f"{Fore.CYAN}|  |    |-- nSensors (Integer)           |\n"
          f"{Fore.CYAN}|  |    |-- nActuators (Integer)         |\n"
          f"{Fore.CYAN}|  |    |-- dateAndTime (Timestamp)      |\n"
          f"{Fore.CYAN}|  |    |-- upTime (Timestamp)           |\n"
          f"{Fore.CYAN}|  |    |-- lastTimeUpdated (Timestamp)  |\n"
          f"{Fore.CYAN}|  |    |-- operationalStatus (Integer)  |\n"
          f"{Fore.CYAN}|  |    |-- reset (Integer)              |\n"
          f"{Fore.CYAN}|  |-- sensors (Table)                   |\n"
          f"{Fore.CYAN}|  |    |-- id (String)                  |\n"
          f"{Fore.CYAN}|  |    |-- type (String)                |\n"
          f"{Fore.CYAN}|  |    |-- status (Integer)             |\n"
          f"{Fore.CYAN}|  |    |-- minValue (Integer)           |\n"
          f"{Fore.CYAN}|  |    |-- maxValue (Integer)           |\n"
          f"{Fore.CYAN}|  |    |-- lastSamplingTime (Timestamp) |\n"
          f"{Fore.CYAN}|  |-- actuators (Table)                 |\n"
          f"{Fore.CYAN}|       |-- id (String)                  |\n"
          f"{Fore.CYAN}|       |-- type (String)                |\n"
          f"{Fore.CYAN}|       |-- status (Integer)             |\n"
          f"{Fore.CYAN}|       |-- minValue (Integer)           |\n"
          f"{Fore.CYAN}|       |-- maxValue (Integer)           |\n"
          f"{Fore.CYAN}|       |-- lastControlTime (Timestamp)  |\n"
          f"{Fore.CYAN}-----------------------------------------\n")
    print(f"\n{Fore.CYAN}Main Menu Options:\n"
          f"{Fore.CYAN}1. Send Message: Send a GET or SET message to the agent.\n"
          f"{Fore.CYAN}2. Status All Devices: Query the status of all devices.\n"
          f"{Fore.CYAN}3. Query Specific Device Status: Query the status of a specific device.\n"
          f"{Fore.CYAN}4. Refresh Agents: Discover agents on the network.\n"
          f"{Fore.CYAN}5. Toggle Detailed Response: Enable/Disable detailed response display.\n"
          f"{Fore.CYAN}6. Tutorial: Show this tutorial.\n"
          f"{Fore.CYAN}7. Exit: Exit the program.\n\n"
          f"{Fore.CYAN}Sending a Message:\n"
          f"{Fore.CYAN}Message Type: 'G' for GET or 'S' for SET\n"
          f"{Fore.CYAN}IID List: Comma-separated list of IIDs (e.g., id,type,beaconRate)\n"
          f"{Fore.CYAN}Value List: Comma-separated list of values (leave blank for GET requests)\n"
          f"{Fore.CYAN}Example to GET id and type of device_1: Type: G, Device ID: device, IIDs: id,type\n"
          f"{Fore.CYAN}Example to SET beaconRate of device_1: Type: S, Device ID: device, IIDs: beaconRate, Values: 20\n")
    input(f"{Fore.YELLOW}Press Enter to return to the Main Menu...")

def toggle_detailed_response():
    global show_detailed_response
    show_detailed_response = not show_detailed_response
    status = "enabled" if show_detailed_response else "disabled"
    print(f"{Fore.GREEN}Detailed response display is now {status}.")

def menu():
    device_ids = extract_device_ids(json_data)
    while True:
        print(f"\n{Fore.GREEN}Main Menu:\n"
              f"{Fore.MAGENTA}1. {Fore.BLUE}Send Message\n"
              f"{Fore.MAGENTA}2. {Fore.BLUE}Status All Devices\n"
              f"{Fore.MAGENTA}3. {Fore.BLUE}Query Specific Device Status\n"
              f"{Fore.MAGENTA}4. {Fore.BLUE}Refresh Agents\n"
              f"{Fore.MAGENTA}5. {Fore.BLUE}Toggle Detailed Response\n"
              f"{Fore.MAGENTA}6. {Fore.BLUE}Tutorial\n"
              f"{Fore.MAGENTA}7. {Fore.BLUE}Exit")
        choice = input(f"{Fore.YELLOW}Enter your choice:{Fore.WHITE} ")
        if choice == '1':
            message_type = input(f"\n{Fore.BLUE}Enter Message Type (G/S): ").upper()  # Ensure the type is uppercase
            device_id = input(f"{Fore.BLUE}Enter Device ID ({', '.join(device_ids)}): ")
            if device_id not in device_ids:
                print(f"{Fore.RED}Invalid Device ID. Please try again.")
                continue
            iids = input(f"{Fore.BLUE}Enter IID List (comma separated): ")
            values = input(f"{Fore.BLUE}Enter Value List (comma separated): ")
            send_message(message_type, device_id, iids, values)
        elif choice == '2':
            for device_id in device_ids:
                query_device_status(device_id)
        elif choice == '3':
            device_id = input(f"\n{Fore.BLUE}Enter Device ID ({', '.join(device_ids)}): ")
            if device_id not in device_ids:
                print(f"{Fore.RED}Invalid Device ID. Please try again.")
                continue
            query_device_status(device_id)
        elif choice == '4':
            agents = send_discovery_pdu()
            if agents:
                for agent in agents:
                    print(f"{Fore.GREEN}Agent {agent} is active")
            else:
                print(f"{Fore.RED}No agents found.")
        elif choice == '5':
            toggle_detailed_response()
        elif choice == '6':
            show_tutorial()
        elif choice == '7':
            print(f"{Fore.RED}Exiting...")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.")

if __name__ == "__main__":
    menu()
