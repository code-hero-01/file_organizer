from classifier import Classifier
from file_scanner import file_scanner
from ui import get_input


def main():
    rules = get_input()
    classifier = Classifier(rules)

    dir_path = "C:/Users/Pranav/Downloads"
    files = file_scanner(dir_path)

    for file in files:
        res = classifier.classify(file)
        print(file.filename + '.' + file.extension + " -> ", res.folder, res.score, res.confidence, res.status, res.alternatives)
        

if __name__ == "__main__":
    main()