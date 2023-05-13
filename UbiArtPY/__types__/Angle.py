import math

class Angle:
    Value: float

    def __init__(self, angle: float, degree: bool = False):
        angle = float(angle)  # Cast value to float
        if degree:
            self.SetDegree(angle)
        else:
            self.SetRadian(angle)
    
    def __str__(self):
        return str(self.Value)
    
    # eq

    def SetDegree(self, angle: float):
        self.Value = angle * math.pi / 180
    
    def SetRadian(self, angle: float):
        self.Value = angle
    
    def ToDegree(self):
        return 180.0 * self.Value / math.pi
    
    def ToRadian(self):
        return self.Value