from dataclasses import dataclass

from .LocalisationId import LocalisationId
from .Path import Path


@dataclass
class LocalizedPath:
    loc_id: LocalisationId
    default_path: Path
