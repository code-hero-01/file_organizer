from pathlib import Path
from models import FileInfo
import re

def file_scanner(dir_path: str) -> list[FileInfo]:
    dir_path = Path(dir_path)

    # check if it is a directory
    if dir_path.is_dir() is False:
        print("Enter a valid directory path!")
        return None

    files = []

    # iterate over files in the directory path
    for f in dir_path.iterdir():
        if f.is_file():
            filename = f.stem
            extension = f.suffix[1:]
            tokens = re.split(r'[^a-zA-Z0-9]+', filename.lower())
            
            file = FileInfo(
                filename= filename,
                extension= extension,
                tokens= tuple(tokens)
            )

            files.append(file)

    return files