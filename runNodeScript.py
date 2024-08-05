import subprocess

class Parser:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                value = Parser(value)
            self.__dict__[key] = value

# Function to run the Node.js script
def run_node_script(value, contents):
    result = subprocess.run(
        ['node', 'start.js', '--value', str(value), '--conts', ','.join([str(c) for c in contents])],
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
    
if __name__ == "__main__":
    import json
    # Run the Node.js script and capture its output
    value = 0
    contents = [23, 10, 8, 16, 13, 3, 22, 13, 18]
    output = run_node_script(value, contents)

    if output:
        print("Output from Node.js script:")
        print(output)
        # Parse the output to extract values if needed
        json_output = Parser(json.loads(output))
        print("Parsed output:")
        print(json_output)

        steamProduction = json_output.steamProduction
        print(steamProduction)