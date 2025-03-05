from dataclasses import dataclass
from typing import SupportsInt


@dataclass(frozen=True)
class JdVersion:
    number: int
    name: str
    alias: str

    def __str__(self):
        return self.alias

    def __int__(self):
        return self.number


# All JD Versions
Jd1 = JdVersion(name="Just Dance", alias="JD1", number=1)
Jd2 = JdVersion(name="Just Dance 2", alias="JD2", number=2)
Jd3 = JdVersion(name="Just Dance 3", alias="JD3", number=3)
Jd4 = JdVersion(name="Just Dance 4", alias="JD4", number=4)
Jd2014 = JdVersion(name="Just Dance 2014", alias="JD2014", number=2014)
Jd2015 = JdVersion(name="Just Dance 2015", alias="JD2015", number=2015)
Jd2016 = JdVersion(name="Just Dance 2016", alias="JD2016", number=2016)
Jd2017 = JdVersion(name="Just Dance 2017", alias="JD2017", number=2017)
Jd2018 = JdVersion(name="Just Dance 2018", alias="JD2018", number=2018)
Jd2019 = JdVersion(name="Just Dance 2019", alias="JD2019", number=2019)
Jd2020 = JdVersion(name="Just Dance 2020", alias="JD2020", number=2020)
Jd2021 = JdVersion(name="Just Dance 2021", alias="JD2021", number=2021)
Jd2022 = JdVersion(name="Just Dance 2022", alias="JD2022", number=2022)
JdNext = JdVersion(name="Just Dance Next", alias="JDNEXT", number=3333)
JdUnlimited = JdVersion(name="Just Dance Unlimited", alias="JDU", number=9999)
JdKids = JdVersion(name="Just Dance Kids", alias="Kids", number=123)
JdAbba = JdVersion(name="ABBA: You Can Dance", alias="ABBA", number=4884)
JdIgnored = JdVersion(name="Ignored", alias="Ignored", number=100)
JdInvalid = JdVersion(name="Invalid", alias="Invalid", number=0)
All = Jd1, Jd2, Jd3, Jd4, Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited, JdKids, JdAbba, JdIgnored, JdInvalid


def from_number(number: SupportsInt) -> JdVersion:
    for ver in All:
        if ver.number == number:
            return ver
    return JdInvalid


def from_short_name(shortname: str) -> JdVersion:
    for ver in All:
        if ver.alias == shortname:
            return ver
    return JdInvalid


def from_name(name: str) -> JdVersion:
    for ver in All:
        if ver.name == name:
            return ver
    return JdInvalid
