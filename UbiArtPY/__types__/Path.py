import os

class Path:
    strId: str
    
    def __init__(self, strId: str = ''):
        self.strId = strId
    
    @staticmethod
    def isValid(path: str) -> bool:
        return os.path.exists(path)
    def getAbsolute(self):
        return self.strId
    def __str__(self) -> str:
        return self.strId.replace('\\', '/')
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return __value.lower() == self.strId.lower()
        if isinstance(__value, Path):
            return __value.strId.lower() == self.strId.lower()
        return False