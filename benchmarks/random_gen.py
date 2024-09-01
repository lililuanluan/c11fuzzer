import random

def generate_random_numbers(n):
    num = [random.randint(1, 4294967295) for _ in range(n)]
    return num

def main():
    n = 3000
    random_numbers = generate_random_numbers(n)
    print("Seeds=({})".format(' '.join(map(str, random_numbers))))
    
    
    
if __name__ == "__main__":
    random.seed(114514)
    main()