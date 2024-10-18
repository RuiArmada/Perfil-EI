import subprocess
import yaml
import os

def run_bots_sequentially(config_file):
    # Load the configuration from a YAML file for the Python script
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    # Iterate over each bot configuration and run them sequentially
    for bot in config['bots']:
        print(f"Starting bot: {bot['name']} using command: {bot['command']}\n\n")

        # Get the working directory from the config file
        cwd = bot['directory']
        
        # Start the process with the correct working directory
        process = subprocess.Popen(bot['command'], cwd=cwd, shell=True)
        
        # Wait for the bot process to complete
        process.wait()
        
        print(f"\n\nBot {bot['name']} has completed. Checking for the next bot...\n\n")

# Example usage assuming the Python script's config file is in the same folder as the script
run_bots_sequentially('bots.yaml')
