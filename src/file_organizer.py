from models import Status, FileInfo, ClassificationResult
from pathlib import Path
import shutil

class FileOrganizer:
    def __init__(self, root: str, results: dict):
        self.root = Path(root)
        self.results = results
        self.plan = {}
        self.create_plan()

    def create_plan(self):
        for file, res in self.results.items():
            source_file = self.root / (file.filename + '.' + file.extension)
           
            destination_dr = ""
            if res.status == Status.UNKNOWN:
                destination_dr = self.root

            elif res.status == Status.AMBIGUOUS:
                destination_dr = self.handle_ambiguous(file, res)

            elif res.status == Status.ASSIGNED:
                destination_dr = self.root / res.folder

            self.plan[source_file] = destination_dr
            
    def handle_ambiguous(self, file: FileInfo, res: ClassificationResult) -> Path:
        print(f"{file.filename}.{file.extension} - Ambiguous Status")
        print(f"Press 1 to select {res.alternatives[0]}")
        print(f"Press 2 to select {res.alternatives[1]}")
        print(f"Press 3 to not move file")

        option = int(input())

        destination_path = ""
        match option:
            case 1:
                destination_path = self.root / res.alternatives[0]
            case 2:
                destination_path = self.root / res.alternatives[1]
            case 3:
                destination_path = self.root

        return destination_path


    def organize(self):
        for source_file, destination_dir in self.plan.items():
            print(f"{source_file} -> {destination_dir}")
            # shutil.move(source_file, destination_dir)

        print("Successfully organized files")