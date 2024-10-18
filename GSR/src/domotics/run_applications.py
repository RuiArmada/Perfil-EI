import subprocess
import os

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    agent_path = os.path.join(base_path, 'agent.py')
    manager_path = os.path.join(base_path, 'manager.py')
    
    agent_process = subprocess.Popen(['python', agent_path])
    manager_process = subprocess.Popen(['python', manager_path])

    try:
        agent_process.wait()
        manager_process.wait()
    except KeyboardInterrupt:
        agent_process.terminate()
        manager_process.terminate()
        print("Applications terminated.")

if __name__ == "__main__":
    main()
