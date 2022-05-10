def log_to_file(*args):
    with open('logs/logs.txt', 'a') as f:
        print(*args, file=f)
