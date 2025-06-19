# Main package initialization

ROOT_DIR = None

def set_root_dir(path: str):
    global ROOT_DIR
    from pathlib import Path
    ROOT_DIR = Path(path).resolve()
