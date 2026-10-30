from models import FileInfo, Status, ClassificationResult
from collections import defaultdict
import math

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
                    res.status = Status.UNKNOWN

            else:
                confidence = ((first_highest[1] - second_highest[1]) / first_highest[1]) * 100

                if confidence >= 75:
                    res.folder = first_highest[0] 
                    res.score = first_highest[1]
                    res.status = Status.ASSIGNED
                    res.alternatives = (second_highest[0],)
                   
                elif confidence < 75 and confidence >= 40:
                    res.folder = None
                    res.status = Status.AMBIGUOUS
                    res.alternatives = (first_highest[0], second_highest[0])
                else:
                    res.folder = None
                    res.status = Status.UNKNOWN

        elif len(scores) == 1:
            confidence = 100
            if (scores[0][1] >= 30):
                res.folder = scores.items()[0][0]
                res.status = Status.ASSIGNED
            else:
                res.folder = None
                res.status = Status.UNKNOWN

        res.confidence = confidence
        return res