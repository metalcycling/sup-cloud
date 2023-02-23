"""
Utility functions
"""

# Headers
import subprocess

# Functions
def bash(command, stdout = False):
    """
    - Run bash commands as if they are directly typed on the shell and return response
    - Print 'stdout' if 'stdout = True'
    """
    proc = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)
    response = []

    for encoded in proc.stdout.readlines():
        decoded = encoded.decode("utf-8") 

        if decoded[-1] == '\n':
            response.append(decoded[:-1])
        else:
            response.append(decoded)

    if stdout:
        for line in response:
            print(line)

    return response
