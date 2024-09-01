import os
import subprocess

# run_command_sync_stdout = True
run_command_sync_stdout = False

def run_command(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output = ""
        for line in iter(process.stdout.readline, ''):
            if run_command_sync_stdout == True:
                print(line.strip())
            output += line
        process.stdout.close()
        return_code = process.wait()
        if return_code != 0:
            print(f"{command} failed with return code {return_code}")
            input()
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(e.output)
        return None
