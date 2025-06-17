def split_full_name(full_name):
    parts = full_name.strip().split()
    if len(parts) > 1:
        first_name = parts[-1]
        last_name = ' '.join(parts[:-1])
    else:
        first_name = full_name
        last_name = ''
    return first_name, last_name