import os

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def join(*parts):
    return os.path.join(*parts)
