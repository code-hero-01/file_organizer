from pathlib import Path
import re

class FileInfo:
    def __init__(self, filename : str, extension : str):
        self.filename = filename
        self.extension = extension
        self.tokens = re.split(r'[^a-zA-Z0-9]+', filename.lower())

        self.assigned_folder = None
        self.score = 0
        self.confidence = 0 
        self.status = None
        self.alternatives = []

class Rule:
    def __init__(self, folder_name : str, keywords : list, extensions : list):
        self.folder_name = folder_name
        self.keywords = {keyword.lower() for keyword in keywords}
        self.extensions = {extension.lower() for extension in extensions}

class Classifier:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule : Rule):
        self.rules.append(rule)

    def classify(self, file : FileInfo) :
        scores = {}

        for rule in self.rules:
            scores[rule.folder_name] = 0

            for keyword in rule.keywords:
                if keyword in file.tokens:
                    scores[rule.folder_name] += 20
            for extension in rule.extensions:
                if extension == file.extension:
                    scores[rule.folder_name] += 10

        confidence = 0
        if len(scores) > 1:
            top_two_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:2]
            first_highest = top_two_items[0]
            second_highest = top_two_items[1]

            if first_highest[1] == 0:
                    file.assigned_folder = None
                    file.status = "unknown"

            else:
                confidence = ((first_highest[1] - second_highest[1]) / first_highest[1]) * 100

                if confidence >= 75:
                    file.assigned_folder = first_highest[0] 
                    file.score = first_highest[1]
                    file.status = "assigned"
                    file.alternatives = [second_highest[0]]
                elif confidence < 75 and confidence >= 40:
                    file.assigned_folder = None
                    file.status = "ambiguous"
                    file.alternatives = [first_highest[0], second_highest[0]]
                else:
                    file.assigned_folder = None
                    file.status = "unknown"

        elif len(scores) == 1:
            confidence = 100
            if (scores.items()[0][1] >= 30):
                file.assigned_folder = scores.items()[0][0]
                file.status = "assigned"
            else:
                file.assigned_folder = None
                file.status = "unknown"

        file.confidence = confidence

def user_input(classifier : Classifier):
    while True:
        print('Press 1 to add a new folder')
        print('Press 2 to exit')
        option = int(input())
        match option:
            case 1:
                folder_name = input("Enter folder name: ")
                keywords = input("Enter keywords to match separated by spaces: ").split(' ')
                extensions = input("Enter names of extensions to match separated by spaces: ").split(' ')
                rule = Rule(folder_name, keywords, extensions)
                classifier.add_rule(rule)

            case 2:
                break

def main():
    directory = Path("C:/Users/Pranav/Downloads")

    classifier = Classifier()
    user_input(classifier)
    if (len(classifier.rules) == 0):
        rule1 = Rule('pics', ['photo', 'screenshot', 'pic', 'picture'], ['jpg', 'jpeg', 'png', 'webp'])
        classifier.add_rule(rule1)

        rule2 = Rule('docs', ['document', 'doc', 'college', 'homework', 'assignment', 'assign', 'ass', '24106007'], ['pdf', 'docx', 'ppt', 'md', 'xlsx', 'py', 'cpp', 'c'])
        classifier.add_rule(rule2)

    files = []
    for path in directory.iterdir():
        if path.is_file():
            file = FileInfo(path.stem, path.suffix[1:])
            files.append(file)

    for file in files:
        classifier.classify(file)
        print(file.filename + '.' + file.extension)
        print("-> ", file.assigned_folder, file.score, file.confidence, file.status, file.alternatives)
        

if __name__ == "__main__":
    main()