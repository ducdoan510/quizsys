import random
import string

DEFAUT_CHAR_STRING = string.ascii_lowercase + string.digits

def generate_random_string(chars=DEFAUT_CHAR_STRING, size=6):
    return ''.join(random.choice(chars) for _ in range(size))
