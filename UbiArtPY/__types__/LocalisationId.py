from dataclasses import dataclass

from .__base__ import uint32


@dataclass(frozen=True)
class LocalisationId:
    loc_id: uint32 = 0xffffffff

    def __str__(self) -> str:
        return str(self.loc_id)

    def __int__(self) -> int:
        return int(self.loc_id)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, LocalisationId):
            return __value.loc_id == self.loc_id
        if isinstance(__value, int):
            return __value == self.loc_id
        return False
