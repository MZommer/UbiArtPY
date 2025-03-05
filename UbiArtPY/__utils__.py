import os
import shutil
import subprocess


def system(cmd: str, stdout: bool = False):
    # TODO: add logger level
    subprocess.check_call(cmd, stdout=None if stdout else subprocess.DEVNULL, stderr=subprocess.STDOUT)


# decorator for creating a temp folder and after using it, delete it
def use_temp(func):
    def wrapper(*args, **kwargs):
        exists_temp = os.path.isdir("/temp/")
        if not exists_temp:
            os.mkdir("/temp/")
        func(*args, **kwargs)
        if not exists_temp:
            shutil.rmtree("/temp/")

    return wrapper


class InvalidFileError(Exception):
    def __init__(self, message="Invalid file!"):
        self.message = message
        super().__init__(self.message)
