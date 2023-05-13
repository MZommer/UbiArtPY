from dataclasses import dataclass

@dataclass(frozen=True)
class JdVersion:
    Number: int
    Name: str
    ShortName: str

    def __str__(self):
        return self.ShortName
    def __int__(self):
        return self.Number


# All JD Versions
Jd1 = JdVersion(Name = "Just Dance", ShortName = "JD1", Number = 1)
Jd2 = JdVersion(Name = "Just Dance 2", ShortName = "JD2", Number = 2)
Jd3 = JdVersion(Name = "Just Dance 3", ShortName = "JD3", Number = 3)
Jd4 = JdVersion(Name = "Just Dance 4", ShortName = "JD4", Number = 4)
Jd2014 = JdVersion(Name = "Just Dance 2014", ShortName = "JD2014", Number = 2014)
Jd2015 = JdVersion(Name = "Just Dance 2015", ShortName = "JD2015", Number = 2015)
Jd2016 = JdVersion(Name = "Just Dance 2016", ShortName = "JD2016", Number = 2016)
Jd2017 = JdVersion(Name = "Just Dance 2017", ShortName = "JD2017", Number = 2017)
Jd2018 = JdVersion(Name = "Just Dance 2018", ShortName = "JD2018", Number = 2018)
Jd2019 = JdVersion(Name = "Just Dance 2019", ShortName = "JD2019", Number = 2019)
Jd2020 = JdVersion(Name = "Just Dance 2020", ShortName = "JD2020", Number = 2020)
Jd2021 = JdVersion(Name = "Just Dance 2021", ShortName = "JD2021", Number = 2021)
Jd2022 = JdVersion(Name = "Just Dance 2022", ShortName = "JD2022", Number = 2022)
Jd2022 = JdVersion(Name = "Just Dance Next", ShortName = "JDNEXT", Number = 3333)
JdUnlimited = JdVersion(Name = "Just Dance Unlimited", ShortName = "JDU", Number = 9999)
JdKids = JdVersion(Name = "Just Dance Kids", ShortName = "Kids", Number = 123)
JdAbba = JdVersion(Name = "ABBA: You Can Dance", ShortName = "ABBA", Number = 4884)
JdIgnored = JdVersion(Name = "Ignored", ShortName = "Ignored", Number = 100)
JdInvalid = JdVersion(Name = "Invalid", ShortName = "Invalid", Number = 0)
All = Jd1, Jd2, Jd3, Jd4, Jd2014, Jd2015, Jd2016, Jd2017, Jd2018, Jd2019, Jd2020, Jd2021, Jd2022, JdUnlimited, JdKids, JdAbba, JdIgnored, JdInvalid

def FromNumber(number):
    for ver in All:
        if ver.Number == number:
            return ver
    return JdInvalid

def FromShortName(shortname):
    for ver in All:
        if ver.ShortName == shortname:
            return ver
    return JdInvalid

def FromName(name):
    for ver in All:
        if ver.Name == name:
            return ver
    return JdInvalid
