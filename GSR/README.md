# Home Automation System

## Overview

This Python-based project simulates a home automation system using a simplified version of the SNMP protocol, referred to as L-SNMPvS. The system includes virtual devices for monitoring light intensity and temperature, and controlling lights and air conditioning. It also provides a command-line interface (CLI) to interact with these virtual devices.

## Project Structure

```
GSR/
├── src/
|   ├──setup.py
│   └── domotics/
│       ├── __init__.py
│       ├── agent.py
│       ├── data_store.py
│       ├── manager.py
│       ├── mib_loader.py
│       ├── mib.json
│       ├── pdu.py
│       ├── run_applications.py
│       ├── security.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Modules

### 1. `agent.py`

The agent module simulates a device agent that handles SNMP-like GET and SET requests. It processes the requests and returns the appropriate responses.

### 2. `manager.py`

The manager module provides a CLI for interacting with the virtual devices. Users can check device status and set values for temperature and light intensity.

### 3. `data_store.py`

Handles the storage and retrieval of data for the virtual devices.

### 4. `mib_loader.py`

Loads and processes the Management Information Base (MIB) data from a JSON file.

### 5. `pdu.py`

Defines the protocol data units (PDUs) used for communication between the manager and agent.

### 6. `security.py`

Provides encryption and decryption functionalities to ensure secure communication.


## Setup

### Prerequisites

- Python 3.8 or later

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/home_automation.git
   cd home_automation
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv domotics_env
   source domotics_env/bin/activate  # On Windows use `domotics_env\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Run the Agent**:
   ```bash
   python src/domotics/agent.py
   ```

2. **Run the Manager**:
   Open another terminal and run:
   ```bash
   python src/domotics/manager.py
   ```

### Generating Keys for Secure Communication

Keys for encryption and decryption are generated automatically if they do not exist.

## Example Usage

1. **Start the CLI**:
   ```bash
   python src/domotics/manager.py
   ```

2. **Set the maximum temperature for a specific sensor**:
   ```plaintext
   Main Menu:
   1. Send Message
   2. Status All Devices
   3. Query Specific Device Status
   4. Refresh Agents
   5. Toggle Detailed Response
   6. Tutorial
   7. Exit
   Enter your choice: 1

   Enter Message Type (G/S): S
   Enter Device ID (device, device_2, device_3): device
   Enter IID List (comma separated): sensors.maxValue
   Enter Value List (comma separated): 1000

   Received response from ('127.0.0.1', 5000):
   Tag: kdk847ufh84jg87g
   Type: R
   Timestamp: 21:07:2024:19:56:50
   Message Identifier: H41VRA3UVOFE14BB
   IIDs:
   Values:
   Errors: 0
   ```

3. **Verify the change**:
   ```plaintext
   Main Menu:
   1. Send Message
   2. Status All Devices
   3. Query Specific Device Status
   4. Refresh Agents
   5. Toggle Detailed Response
   6. Tutorial
   7. Exit
   Enter your choice: 1

   Enter Message Type (G/S): G
   Enter Device ID (device, device_2, device_3): device
   Enter IID List (comma separated): sensors.maxValue
   Enter Value List (comma separated):

   Received response from ('127.0.0.1', 5000):
   Tag: kdk847ufh84jg87g
   Type: R
   Timestamp: 21:07:2024:19:57:10
   Message Identifier: POAACRK8BSN5I9X5
   IIDs: sensors_1.maxValue,sensors_2.maxValue
   Values: 1000,1000
   Errors: 0
   ```

## Troubleshooting

If you encounter issues with processes not starting, ensure the following:

1. **Supervision Tree**: Verify that the `agent.py` and `manager.py` modules are running correctly.
2. **Process Registration**: Confirm that the sockets are bound correctly and are accessible.
3. **Application Configuration**: Check that all necessary keys and configurations are set up correctly.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.
