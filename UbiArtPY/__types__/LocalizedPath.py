from dataclasses import dataclass
from .Path import Path
from .LocalisationId import LocalisationId

@dataclass
class LocalizedPath:
    LocID: LocalisationId
    DefaultPath: Path
