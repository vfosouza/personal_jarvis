from pathlib import Path
from config import SUPPORTED_EXTENSIONS, IGNORE_DIRS, MAX_FILE_SIZE

def load_files(root_path: str):
    print(f"Scanning {root_path}")
    for file in Path(root_path).rglob("*"):
        print(f"Found: {file}")
        if not file.is_file():
            continue
        if any(ignored in file.parts for ignored in IGNORE_DIRS):
            continue
        if file.suffix not in SUPPORTED_EXTENSIONS:
            continue
        if file.name.startswith("."):
            continue
        if file.stat().st_size > MAX_FILE_SIZE:  # Ignorar arquivos muito grandes
            print(f"File {file} exceeds max size of {MAX_FILE_SIZE} bytes. Skipping.")
            continue

        content = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        yield file, content