import random
import string

def generate_random_password(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def split_full_name(full_name):
    if not full_name:
        return "", "" 
    parts = full_name.strip().split()
    if len(parts) > 1:
        first_name = parts[-1]
        last_name = ' '.join(parts[:-1])
    else:
        first_name = full_name
        last_name = ''
    return first_name, last_name