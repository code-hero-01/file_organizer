from pathlib import Path
import re
from collections import defaultdict
import math


class FileInfo:
    def __init__(self, filename : str, extension : str):
        self.filename = filename
        self.extension = extension
        self.tokens = re.split(r'[^a-zA-Z0-9]+', filename.lower())


class Rule:
    def __init__(self, folder_name : str, keywords : list, extensions : list):
        self.folder_name = folder_name
        self.keywords = {keyword.lower() for keyword in keywords}
        self.extensions = {extension.lower() for extension in extensions}


class ClassificationResult:
    def __init__(self):
        self.folder = None
        self.score = 0
        self.confidence = None
        self.status = "unknown"
        self.alternatives = []


class Classifier:
    def __init__(self, rulesList : list):
        self.rules = rulesList

        self.keyword_inverted_idx = defaultdict(list)
        self.extension_inverted_idx = defaultdict(list)
        for rule in self.rules: 
            for keyword in rule.keywords:
                self.keyword_inverted_idx[keyword].append(rule.folder_name)
            for extension in rule.extensions:
                self.extension_inverted_idx[extension].append(rule.folder_name)


    def score(self, file : FileInfo) -> dict:
        scores = {}
        total_folders = len(self.rules)

        keyword_idf_idx = {}
        extension_idf_idx = {}

        for keyword, folders in self.keyword_inverted_idx.items():
            keyword_idf_idx[keyword] = math.log((total_folders + 1)/ (len(set(folders)) + 1)) + 1
        for extension, folders in self.extension_inverted_idx.items():
            extension_idf_idx[extension] = math.log((total_folders + 1) / (len(set(folders)) + 1)) + 1

        keyword_wt = 1
        extension_wt = 1
        for rule in self.rules:
            keyword_score = 0
            for keyword in rule.keywords:
                if keyword in file.tokens:
                    keyword_score += keyword_idf_idx[keyword]

            extension_score = 0
            if file.extension in rule.extensions:
                extension_score = extension_idf_idx[file.extension]

            scores[rule.folder_name] = keyword_wt * keyword_score + extension_wt * extension_score

        return scores

    def classify(self, file : FileInfo) -> ClassificationResult:
        scores = {}
        res = ClassificationResult()

        scores = self.score(file)

        confidence = 0
        if len(scores) > 1:
            top_two_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:2]
            first_highest = top_two_items[0]
            second_highest = top_two_items[1]

            if first_highest[1] == 0:
                    res.folder = None
                    res.status = "unknown"

            else:
                confidence = ((first_highest[1] - second_highest[1]) / first_highest[1]) * 100

                if confidence >= 75:
                    res.folder = first_highest[0] 
                    res.score = first_highest[1]
                    res.status = "assigned"
                    res.alternatives = [second_highest[0]]
                elif confidence < 75 and confidence >= 40:
                    res.folder = None
                    res.status = "ambiguous"
                    res.alternatives = [first_highest[0], second_highest[0]]
                else:
                    res.folder = None
                    res.status = "unknown"

        elif len(scores) == 1:
            confidence = 100
            if (scores.items()[0][1] >= 30):
                res.folder = scores.items()[0][0]
                file.status = "assigned"
            else:
                res.assigned_folder = None
                res.status = "unknown"

        res.confidence = confidence
        return res


def user_input(rules : list):
    while True:
        print('Press 1 to add a new folder')
        print('Press 2 to classify')
        option = int(input())
        match option:
            case 1:
                folder_name = input("Enter folder name: ")
                keywords = input("Enter keywords to match separated by spaces: ").split(' ')
                extensions = input("Enter names of extensions to match separated by spaces: ").split(' ')
                rule = Rule(folder_name, keywords, extensions)
                rules.append(rule)

            case 2:
                break


def main():
    directory = Path("C:/Users/Pranav/Downloads")

    rules = []
    user_input(rules)
    rules.append(Rule('pics', ['photo', 'screenshot', 'pic', 'picture'], ['jpg', 'jpeg', 'png', 'webp']))
    rules.append(Rule('docs', ['document', 'doc'], ['pdf', 'docx', 'pptx', 'md', 'xlsx', 'py', 'cpp', 'c']))
    rules.append(Rule('college', ['document', 'doc', 'college', 'homework', 'assignment', 'assign', 'ass', '24106007'], ['pdf', 'docx', 'ppt', 'md']))
    rules.append(Rule('videos', ['movie', 'film', 'clip', 'season', 'episode'], ['mp4', 'mkv', 'webm', 'avi']))
    rules.append(Rule('audio', ['song', 'sound'], ['mp3', 'wav', 'flac', 'opus']))

    classifier = Classifier(rules)

    files = []
    for path in directory.iterdir():
        if path.is_file():
            file = FileInfo(path.stem, path.suffix[1:])
            files.append(file)

    for file in files:
        res = classifier.classify(file)
        print(file.filename + '.' + file.extension + " -> ", res.folder, res.score, res.confidence, res.status, res.alternatives)
        

if __name__ == "__main__":
    main()