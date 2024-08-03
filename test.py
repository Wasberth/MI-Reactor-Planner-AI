import sys
import subprocess
import json

# Function to run the Node.js script
def run_node_script():
    result = subprocess.run(
        ['node', 'start.js', '--value', '0', '--conts', '0,0,0,0,5,0,0,0,0'],
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode == 0:
        return result.stdout
    else:
        print(f"Error running script: {result.stderr}")
        return None

# Run the Node.js script and capture its output
output = run_node_script()

if output:
    print("Output from Node.js script:")
    print(output)
    # Parse the output to extract values if needed
    json_output = json.loads(output)
    print("Parsed output:")
    print(json_output)