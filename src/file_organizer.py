from pathlib import Path
import shutil


def organize_files(plan: dict[Path, Path | None]) -> dict[str, list]:
    """Execute an already-approved plan.

    A None destination means leave the file where it is. Existing destination
    files are never overwritten. 
    """
    report = {"moved": [], "skipped": [], "errors": []}

    for source, destination_dir in plan.items():
        source = Path(source)

        if destination_dir is None:
            report["skipped"].append(source)
            continue

        destination_dir = Path(destination_dir)

        if not source.exists() or not source.is_file():
            report["errors"].append((source, "Source file does not exist or is not a file."))
            continue

        # A file already in its requested destination does not need moving.
        try:
            if source.parent.resolve() == destination_dir.resolve():
                report["skipped"].append(source)
                continue

            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / source.name

            if destination.exists():
                report["errors"].append(
                    (source, f"Destination already exists: {destination}")
                )
                continue

            shutil.move(str(source), str(destination))
            report["moved"].append((source, destination))

        except OSError as error:
            report["errors"].append((source, str(error)))

    return report
