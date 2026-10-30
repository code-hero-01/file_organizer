from dataclasses import dataclass, field
from enum import Enum, auto

@dataclass(frozen=True)
class FileInfo:
    filename: str
    extension: str
    tokens: tuple[str] = ()

@dataclass
class Rule:
    folder_name: str
    keywords: list[str] = field(default_factory=list)  
    extensions: list[str] = field(default_factory=list)  

class Status(Enum):
    UNKNOWN = auto()
    AMBIGUOUS = auto()
    ASSIGNED = auto()

@dataclass
class ClassificationResult:
    folder: str = None
    score: int = 0
    confidence: int = None
    status: Status = Status.UNKNOWN
    alternatives: tuple[str] = ()

