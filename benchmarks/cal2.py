import sys

def process_file(filename):
    hash_set = set()
    success_count = 0
    failure_count = 0
    unique_failures = set()
    total_count = 0

    with open(filename, 'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith('HASH'):
                hash_val = line.split()[1]
                hash_set.add(hash_val)
                if i < len(lines) - 1 and lines[i + 1].strip() == 'Aborted. Execution: 1':
                    failure_count += 1
                    if hash_val not in unique_failures:
                        # print("{}".format(total_count))
                        pass
                    unique_failures.add(hash_val)
                else:
                    success_count += 1
                # print(f"{total_count} {len(hash_set)} {len(unique_failures)}")
                total_count += 1
    return hash_set, success_count, failure_count, unique_failures, total_count

def print_statistics(HASH_FILE):
    filename = HASH_FILE
    hash_set, success_count, failure_count, unique_failures, total_count = process_file(filename)

    parts = filename.split("_", 1)
    extracted_part = parts[0]
    print(f"TEST: {extracted_part}")
    print("Total different hashes: {} {:.2f}%".format(len(hash_set), 100 * len(hash_set) / total_count))
    # print("Total successful executions: {} {:.2f}%".format(success_count, 100 * success_count / total_count))
    # for hash_val in hash_set:
    #     print(hash_val)
    print("Total failed executions: {} {:.2f}%".format(failure_count, 100 * failure_count / total_count))
    print("Total different failures: {} {:.2f}%".format(len(unique_failures), 100 * len(unique_failures) / total_count))
    print("Total:", total_count)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    print_statistics(filename)
   

