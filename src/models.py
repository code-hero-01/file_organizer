from dataclasses import dataclass, field
from enum import Enum, auto

@dataclass
class FileInfo:
    filename: str
    extension: str
    tokens: list[str] = field(default_factory=list)  

@dataclass
class Rule:
    folder_name: str
    keywords: list[str] = field(default_factory=list)  
    extensions: list[str] = field(default_factory=list)  

@dataclass
class ClassificationResult:
    folder: str = None
    score: int = 0
    confidence: int = None
    status: str = "unknown"
    alternatives: list[str] = field(default_factory=list)  

class Status(Enum):
            UNKNOWN = auto
            AMBIGUOUS = auto
            ASSIGNED = auto