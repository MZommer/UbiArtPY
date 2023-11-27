from dataclasses import dataclass

@dataclass(frozen=True)
class LocalisationId:
    LocId: int
    
    def __str__(self) -> str:
        return str(self.LocId)
    def __int__(self) -> int:
        return self.LocId
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, LocalisationId):
            return __value.LocId == self.LocId
        if isinstance(__value, int):
            return __value == self.LocId
        return False
