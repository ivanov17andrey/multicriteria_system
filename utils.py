import os


def log_to_file(*args):
    with open(os.path.join(os.path.dirname(__file__), 'logs', 'logs.txt'), 'a') as f:
        print(*args, file=f)
