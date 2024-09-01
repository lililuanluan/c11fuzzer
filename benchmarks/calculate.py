import sys

def calculate_average_execution(file_path):
    total_executions = 0
    num_lines = 0

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Aborted. Execution:"):
                execution = int(line.split(":")[1].strip())
                total_executions += execution
                num_lines += 1

    if num_lines == 0:
        print("No valid execution lines found in the file.")
        return

    average_execution = total_executions / (num_lines+0.0)
    return average_execution

if __name__ == "__main__":
    arguments = sys.argv
    file_path = arguments[1]  
    average = calculate_average_execution(file_path)
    if average is not None:
        print("Average Execution:", average)
