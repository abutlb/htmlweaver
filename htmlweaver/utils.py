import os
from pathlib import Path


def read_file(path: str) -> str:
    """Read a file and return its content."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """Write content to a file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {path}")


def validate_file(path: str, extension: str = None) -> bool:
    """Validate that a file exists and optionally check its extension."""
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return False
    if extension and not path.endswith(extension):
        print(f"❌ Expected a {extension} file, got: {path}")
        return False
    return True


def get_base_name(path: str) -> str:
    """Return filename without extension."""
    return Path(path).stem


def get_output_dir(path: str) -> str:
    """Return the directory of a file."""
    return str(Path(path).parent)
