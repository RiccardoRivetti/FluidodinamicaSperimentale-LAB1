class Wing:
    def __init__(self, airfoil, chord, span, thickness, shape_factor):
        self.airfoil   = airfoil
        self.chord     = chord
        self.span      = span
        self.thickness = thickness # Percentage of chord
        self.surface   = chord*span
        self.volume    = chord*span*chord*thickness
        self.shape_factor = shape_factor

class TestSection:
    def __init__(self, length, width, height, pressure_gradient):
        self.length = length
        self.width  = width
        self.height = height
        self.area   = width*height
        self.pressure_gradient = pressure_gradient