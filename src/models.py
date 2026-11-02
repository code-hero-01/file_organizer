from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


@dataclass(frozen=True)
class FileInfo:
    path: Path
    filename: str
    extension: str
    tokens: tuple[str, ...] = ()


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
    folder: str | None = None
    score: float = 0.0
    confidence: float = 0.0
    status: Status = Status.UNKNOWN
    alternatives: tuple[str, ...] = ()


def create_default_rules() -> list[Rule]:
    """Return a fresh set of the application's starter rules."""
    return [
        Rule("pics", ["photo", "screenshot", "pic", "picture"],
             ["jpg", "jpeg", "png", "webp"]),
        Rule("docs", ["document", "doc"],
             ["pdf", "docx", "pptx", "md", "xlsx", "py", "cpp", "c"]),
        Rule("college",
             ["document", "doc", "college", "homework", "assignment",
              "assign", "ass", "24106007"],
             ["pdf", "docx", "ppt", "md"]),
        Rule("videos", ["movie", "film", "clip", "season", "episode"],
             ["mp4", "mkv", "webm", "avi"]),
        Rule("audio", ["song", "sound"],
             ["mp3", "wav", "flac", "opus"]),
    ]


rules = create_default_rules()
