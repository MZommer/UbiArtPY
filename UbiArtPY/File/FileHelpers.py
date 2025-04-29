import os
from datetime import datetime, timezone
from typing import Union

from ..__types__ import uint64

WINDOWS_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)
SECONDS_BETWEEN_EPOCHS = (datetime(1970, 1, 1, tzinfo=timezone.utc) - WINDOWS_EPOCH).total_seconds()
HUNDRED_NS_MULTIPLIER = 10_000_000  # 10 million = 1 second in Windows timestamp


# Convert to Windows timestamps
def to_windows_timestamp(dt: datetime) -> uint64:
    delta = dt - WINDOWS_EPOCH
    return uint64(delta.total_seconds() * HUNDRED_NS_MULTIPLIER)


def from_timestamp(timestamp: Union[int, float]) -> datetime:
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (OSError, AttributeError) as e:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) if timestamp <= 0 else datetime.now(timezone.utc)


def get_windows_file_timestamps(file_path: os.PathLike) -> tuple[uint64, uint64, uint64]:
    stats = os.stat(file_path)
    creation_time = from_timestamp(stats.st_ctime)
    last_access_time = from_timestamp(stats.st_atime)
    last_modified_time = from_timestamp(stats.st_mtime)

    creation_time_win = to_windows_timestamp(creation_time)
    last_modified_time_win = to_windows_timestamp(last_modified_time)
    last_access_time_win = to_windows_timestamp(last_access_time)

    return creation_time_win, last_modified_time_win, last_access_time_win


def override_timestamps(file_path: os.PathLike, creation_time: int, last_modified_time: int):
    """
    Override file timestamps, converting from Windows filetime to Unix timestamp.
    
    Args:
        file_path: Path to the file
        creation_time: Windows filetime (100-nanosecond intervals since Jan 1, 1601)
        last_modified_time: Windows filetime (100-nanosecond intervals since Jan 1, 1601)
    """
    try:
        # Validate inputs
        if creation_time < 0 or last_modified_time < 0:
            raise ValueError("Timestamps cannot be negative")

        # Convert Windows timestamps to Unix timestamps
        creation_time_unix = (creation_time / HUNDRED_NS_MULTIPLIER) + SECONDS_BETWEEN_EPOCHS
        last_modified_time_unix = (last_modified_time / HUNDRED_NS_MULTIPLIER) + SECONDS_BETWEEN_EPOCHS

        # Set the timestamps
        os.utime(file_path, (creation_time_unix, last_modified_time_unix))

    except (OSError, ValueError) as e:
        raise OSError(f"Failed to set timestamps for {file_path}: {e}")
