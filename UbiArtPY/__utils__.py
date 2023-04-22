import subprocess
import os
import shutil


def system(cmd: str, STDOUT: bool = False):
    # TODO: add logger level
    subprocess.check_call(cmd, stdout=None if STDOUT else subprocess.DEVNULL, stderr=subprocess.STDOUT)


# decorator for creating a temp folder and after using it, delete it
def useTemp(func):
    def wrapper(*args, **kwargs):
        existsTemp = os.path.isdir("/temp/")
        if not existsTemp:
            os.mkdir("/temp/")
        func(*args, **kwargs)
        shutil.rmtree("/temp/")

    return wrapper
