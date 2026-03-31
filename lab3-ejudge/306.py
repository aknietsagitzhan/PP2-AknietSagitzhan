class Rectangle:
    def __init__(self):
        self.l = ""
        self.w = ""
        
    def getArea(self):
        self.l, self.w = map(int, input().split())
    
    def printArea(self):
        print(self.l * self.w)

obj = Rectangle()
obj.getArea()
obj.printArea()