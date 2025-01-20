import os
from datetime import datetime, timezone
from ..__types__ import uint64

WINDOWS_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)
SECONDS_BETWEEN_EPOCHS = (datetime(1970, 1, 1, tzinfo=timezone.utc) - WINDOWS_EPOCH).total_seconds()
HUNDRED_NS_MULTIPLIER = 10_000_000  # 10 million = 1 second in Windows timestamp


# Convert to Windows timestamps
def to_windows_timestamp(dt):
    delta = dt - WINDOWS_EPOCH
    return uint64(delta.total_seconds() * HUNDRED_NS_MULTIPLIER)

def get_windows_file_timestamps(file_path: str) -> tuple[uint64, uint64, uint64]:
    stats = os.stat(str(file_path))
    creation_time = datetime.fromtimestamp(stats.st_birthtime, tz=timezone.utc)
    last_access_time = datetime.fromtimestamp(stats.st_atime, tz=timezone.utc)
    last_modified_time = datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc)

    creation_time_win = to_windows_timestamp(creation_time)
    last_modified_time_win = to_windows_timestamp(last_modified_time)
    last_access_time_win = to_windows_timestamp(last_access_time)

    return creation_time_win, last_modified_time_win, last_access_time_win
