from collections import defaultdict
import math

from models import ClassificationResult, FileInfo, Rule, Status


class Classifier:
    """Rule-based classifier using IDF-inspired keyword/extension weights."""

    def __init__(self, rules_list: list[Rule]):
        self.rules = rules_list
        self.keyword_inverted_idx = defaultdict(list)
        self.extension_inverted_idx = defaultdict(list)

        for rule in self.rules:
            for keyword in rule.keywords:
                self.keyword_inverted_idx[keyword.strip().lower()].append(
                    rule.folder_name
                )
            for extension in rule.extensions:
                normalized = extension.strip().lower().lstrip(".")
                self.extension_inverted_idx[normalized].append(rule.folder_name)

        total_folders = len(self.rules)
        self.keyword_idf = {
            keyword: math.log((total_folders + 1) / (len(set(folders)) + 1)) + 1
            for keyword, folders in self.keyword_inverted_idx.items()
        }
        self.extension_idf = {
            extension: math.log((total_folders + 1) / (len(set(folders)) + 1)) + 1
            for extension, folders in self.extension_inverted_idx.items()
        }

    def score(self, file: FileInfo) -> dict[str, float]:
        scores = {}
        file_tokens = {token.lower() for token in file.tokens}
        file_extension = file.extension.lower().lstrip(".")

        for rule in self.rules:
            keyword_score = sum(
                self.keyword_idf[keyword.lower()]
                for keyword in rule.keywords
                if keyword.lower() in file_tokens
            )

            extension_score = 0.0
            if file_extension in {
                extension.lower().lstrip(".") for extension in rule.extensions
            }:
                extension_score = self.extension_idf[file_extension]

            scores[rule.folder_name] = keyword_score + extension_score

        return scores

    def classify(self, file: FileInfo) -> ClassificationResult:
        scores = self.score(file)
        if not scores:
            return ClassificationResult()

        sorted_scores = sorted(
            scores.items(), key=lambda item: item[1], reverse=True
        )
        alternatives = tuple(folder for folder, _ in sorted_scores)
        best_folder, best_score = sorted_scores[0]

        if len(sorted_scores) == 1:
            confidence = 100.0 if best_score > 0 else 0.0
            if best_score > 0:
                return ClassificationResult(
                    folder=best_folder,
                    score=best_score,
                    confidence=confidence,
                    status=Status.ASSIGNED,
                    alternatives=alternatives,
                )
            return ClassificationResult(
                score=best_score,
                confidence=confidence,
                status=Status.UNKNOWN,
                alternatives=alternatives,
            )

        second_score = sorted_scores[1][1]
        if best_score < 1:
            return ClassificationResult(
                score=best_score,
                confidence=0.0,
                status=Status.UNKNOWN,
                alternatives=alternatives,
            )

        # This is a relative score margin, not a calibrated probability.
        confidence = ((best_score - second_score) / best_score) * 100

        if confidence >= 75:
            status = Status.ASSIGNED
            folder = best_folder
        elif confidence >= 40:
            status = Status.AMBIGUOUS
            folder = None
        else:
            status = Status.UNKNOWN
            folder = None

        return ClassificationResult(
            folder=folder,
            score=best_score,
            confidence=confidence,
            status=status,
            alternatives=alternatives,
        )
