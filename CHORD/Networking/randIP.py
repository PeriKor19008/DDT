import random

def generate_random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

