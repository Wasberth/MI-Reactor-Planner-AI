import sys
import subprocess

# Function to run the Node.js script
def run_node_script():
    result = subprocess.run(
        ['node -v'],
        shell=True,
        text=True  # Return the output as a string
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
    for line in output.splitlines():
        if 'The answer is:' in line:
            value = int(line.split(':')[-1].strip())
            print(f"Extracted value: {value}")