class Rectangle:
    def __init__(self, minX, maxY, maxX, minY):
        self.minX = minX
        self.maxY = maxY
        self.maxX = maxX
        self.minY = minY

    def inRectangle(self, x, y):
        if(self.minX <=  x <= self.maxX and self.minY <= y <= self.maxY):
            return True
        else:
            return False
