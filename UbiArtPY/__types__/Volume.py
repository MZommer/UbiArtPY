import math
from typing import SupportsFloat, Union

from .__base__ import float32
from ..Core import serializable_class


@serializable_class
class Volume:
    db: float32

    def __init__(self, db: SupportsFloat):
        self.db = float32(db)
        if not math.isfinite(db):
            raise ValueError("Volume must be a finite number")

    def clamp(self, min_db: SupportsFloat = -120, max_db: SupportsFloat = 0) -> 'Volume':
        """
        Clamp the volume to a specific range.
        :param min_db: The minimum dB value (default is -120).
        :param max_db: The maximum dB value (default is 0).
        :return: A new Volume instance with the clamped value.
        """
        clamped_db = max(float(min_db), min(float(max_db), float(self.db)))
        return Volume(clamped_db)

    def normalize(self, max_db: SupportsFloat = 0) -> 'Volume':
        """
        Normalize the volume to a specific range.
        :param max_db: The maximum dB value (default is 0).
        :return: A new Volume instance with the normalized value.
        """
        normalized_db = min(float(max_db), float(self.db))
        return Volume(normalized_db)

    def __str__(self):
        return str(self.db)

    def __eq__(self, other) -> bool:
        if isinstance(other, Volume):
            return math.isclose(self.db, other.db)
        if isinstance(other, float):
            return math.isclose(self.db, other)
        return False

    def __sub__(self, other: Union['Volume', SupportsFloat]) -> 'Volume':
        if isinstance(other, Volume):
            return Volume(self.db - other.db)
        return Volume(self.db - float(other))

    def __mul__(self, other: SupportsFloat) -> 'Volume':
        return Volume(self.db * float(other))

    def __truediv__(self, other: SupportsFloat) -> 'Volume':
        return Volume(self.db / float(other))
