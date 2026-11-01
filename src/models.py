from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

@dataclass(frozen=True)
class FileInfo:
    path: Path
    filename: str
    extension: str
    tokens: tuple[str] = ()

@dataclass
class Rule:
    folder_name: str
    keywords: list[str] = field(default_factory=list)  
    extensions: list[str] = field(default_factory=list)

rules = []

rules.append(Rule('pics', ['photo', 'screenshot', 'pic', 'picture'], ['jpg', 'jpeg', 'png', 'webp']))
rules.append(Rule('docs', ['document', 'doc'], ['pdf', 'docx', 'pptx', 'md', 'xlsx', 'py', 'cpp', 'c']))
rules.append(Rule('college', ['document', 'doc', 'college', 'homework', 'assignment', 'assign', 'ass', '24106007'], ['pdf', 'docx', 'ppt', 'md']))
rules.append(Rule('videos', ['movie', 'film', 'clip', 'season', 'episode'], ['mp4', 'mkv', 'webm', 'avi']))
rules.append(Rule('audio', ['song', 'sound'], ['mp3', 'wav', 'flac', 'opus']))
  

class Status(Enum):
    UNKNOWN = auto()
    AMBIGUOUS = auto()
    ASSIGNED = auto()

@dataclass
class ClassificationResult:
    folder: str = None
    score: float = 0.0
    confidence: int | None = None
    status: Status = Status.UNKNOWN
    alternatives: tuple[str] = ()

