from classifier import Classifier
from file_scanner import file_scanner
from ui import get_input
from file_organizer import FileOrganizer


def main():
    rules = get_input()
    classifier = Classifier(rules)

    dir_path = "C:/Users/Pranav/Downloads"
    files = file_scanner(dir_path)

    results = {}
    for file in files:
        res = classifier.classify(file)
        results[file] = res
        # print(file.filename + '.' + file.extension + " -> ", res.folder, res.score, res.confidence, res.status, res.alternatives)

    file_organizer = FileOrganizer(dir_path, results)
    file_organizer.organize()

if __name__ == "__main__":
    main()