# mib_loader.py
import json
import os
from data_store import store_data

# Get the absolute path of the directory containing this script
script_dir = os.path.dirname(__file__)
# Construct the full path to the mib.json file
mib_json_path = os.path.join(script_dir, 'mib.json')

# Load JSON data
with open(mib_json_path) as json_file:
    json_data = json.load(json_file)

# Function to recursively store data
def recursive_store_data(prefix, data):
    for key, value in data.items():
        if isinstance(value, dict) and "VALUE" in value:
            store_data(f"{prefix}.{key}" if prefix else key, value["VALUE"])
        elif isinstance(value, dict):
            recursive_store_data(f"{prefix}.{key}" if prefix else key, value)

# Store the JSON data
recursive_store_data("", json_data)

# At the end of mib_loader.py
if __name__ == "__main__":
    recursive_store_data("", json_data)
    # Print the data_store for debugging
    import pprint
    pprint.pprint(data_store)
