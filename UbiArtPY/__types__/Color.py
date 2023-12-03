from dataclasses import dataclass

@dataclass
class Color:
    A: int = 255
    R: int = 255
    G: int = 255
    B: int = 255
    
    # Constructors
    def __init__(self, *args):
        print(len(args))
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
        if length == 3:  # RGB format
            self.R, self.G, self.B = [int(value[i:i+1]*2, 16) for i in range(0, 3)]
            self.A = 255
        elif length == 4:  # ARGB format
            self.A, self.R, self.G, self.B = [int(value[i:i+1]*2, 16) for i in range(0, 4)]
        elif length == 6:  # RRGGBB format
            self.R, self.G, self.B = [int(value[i:i+2], 16) for i in range(0, 6, 2)]
            self.A = 255
        elif length == 8:  # AARRGGBB format
            self.A, self.R, self.G, self.B = [int(value[i:i+2], 16) for i in range(0, 8, 2)]
        else:
            raise ValueError("Invalid hexadecimal color string")
       
    def _init_argb(self, alpha: int, red: int, green: int, blue: int): # ARGB
        self.A = alpha
        self.R = red
        self.G = green
        self.B = blue

    def _init_rgb(self, red: int, green: int, blue: int): # RGB
        self.A = 255
        self.R = red
        self.G = green
        self.B = blue