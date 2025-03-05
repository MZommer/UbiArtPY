from ..__types__ import uint32, Platform, JdVersion


class Versioning:
    EngineSignature = uint32(490359856)
    Engine = uint32(253653)
    GlobalCache = uint32(2)
    LogicDatabaseCache = uint32(15)
    Texture = uint32(9)
    Sound = uint32(11)
    Soundwich = uint32(1)
    AnimPatchBank = uint32(16)
    AnimTrack = uint32(35)
    AnimSkeleton = uint32(15)
    Game = uint32(6)
    Bundle = uint32(5)
    FriezeConfig = uint32(101)
    Scene = uint32(7)
    Atlas = uint32(18)
    Mesh3D = uint32(5)
    Skeleton3D = uint32(4)
    Animation3D = uint32(7)
    AnimMeshVertex = uint32(10)
    DashMPD = uint32(1)

    @staticmethod
    def set_game(jd_ver: JdVersion, platform: Platform):
        if jd_ver == JdVersion.Jd2014:
            Versioning.EngineSignature = uint32(3883161868)
            Versioning.Engine = uint32(109470)
        elif jd_ver == JdVersion.Jd2015:
            pass
        if jd_ver == JdVersion.Jd2016:
            pass
