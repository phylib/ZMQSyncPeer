class Rectangle:
    def __init__(self, leftUpperX, leftUpperY, rightLowerX, rightLowerY):
        self.leftUpperX = leftUpperX
        self.leftUpperY = leftUpperY
        self.rightLowerX = rightLowerX
        self.rightLowerY = rightLowerY

    def inRectangle(self, x, y):
        if(self.leftUpperX <=  x <= self.rightLowerX and self.rightLowerY <= y <= self.leftUpperY):
            return True
        else:
            return False
