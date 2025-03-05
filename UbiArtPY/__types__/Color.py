from .__base__ import uint8
from ..Core import serializable_class


@serializable_class
class Color:
    A: uint8 = 255
    R: uint8 = 255
    G: uint8 = 255
    B: uint8 = 255

    # Constructors
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            self._init_hex(args[0])
        elif len(args) == 3:
            self._init_rgb(*args)
        elif len(args) == 4:
            self._init_argb(*args)
        else:
            raise ValueError("Invalid color arguments")

    def _init_hex(self, value):
        # Hex string
        value = value.lstrip('#')
        length = len(value)

        if length in (3, 4):  # RGB or ARGB shorthand format
            # Duplicate each character to convert shorthand to full format
            value = ''.join(c * 2 for c in value)
            length = len(value)

        if length == 6:  # RR GG BB format
            # Add the alpha chanel
            value = "FF" + value

        # AA RR GG BB format
        self.A = uint8(int(value[0:2], 16))
        self.R = uint8(int(value[2:4], 16))
        self.G = uint8(int(value[4:6], 16))
        self.B = uint8(int(value[6:8], 16))

    def _init_argb(self, alpha: uint8, red: uint8, green: uint8, blue: uint8):  # ARGB
        self.A = alpha
        self.R = red
        self.G = green
        self.B = blue

    def _init_rgb(self, red: uint8, green: uint8, blue: uint8):  # RGB
        self.A = uint8(255)
        self.R = red
        self.G = green
        self.B = blue

    def __str__(self) -> str:
        return "#" + "".join(f"{v:02X}" for v in (self.R, self.G, self.B, self.A))

    def __repr__(self) -> str:
        return f"Color({self.R}, {self.G}, {self.B}, {self.A})"
