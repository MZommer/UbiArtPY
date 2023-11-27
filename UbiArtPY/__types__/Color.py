from functools import singledispatchmethod

class Color:
    A: int = 255
    R: int = 255
    G: int = 255
    B: int = 255
    
    # Constructors
    @singledispatchmethod
    def __init__(self, value):
        ...
    
    @__init__.register
    def _(self, value: str): # Hex string
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
    
    @__init__.register
    def _(self, alpha: int, red: int, green: int, blue: int): # ARGB
        self.A = alpha
        self.R = red
        self.G = green
        self.B = blue
    
    @__init__.register
    def _(self, red: int, green: int, blue: int): # RGB
        self.A = 255
        self.R = red
        self.G = green
        self.B = blue