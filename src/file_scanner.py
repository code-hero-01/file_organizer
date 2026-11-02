from pathlib import Path
import re

from models import FileInfo


def file_scanner(dir_path: str | Path) -> list[FileInfo]:
    """Return FileInfo objects for files directly inside dir_path.

    Subdirectories are intentionally not scanned recursively.
    Raises NotADirectoryError for an invalid directory and OSError
    if the directory cannot be read.
    """
    directory = Path(dir_path)

    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    files = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file():
            continue

        stem = path.stem
        extension = path.suffix[1:].lower()
        tokens = tuple(
            token for token in re.split(r"[^a-zA-Z0-9]+", stem.lower())
            if token
        )

        files.append(
            FileInfo(
                path=path,
                filename=stem,
                extension=extension,
                tokens=tokens,
            )
        )

    return files
