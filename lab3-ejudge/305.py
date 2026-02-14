class Square:
    def __init__(self):
        self.n = ""

    def getNum(self):
        self.n = int(input())

    def printNum(self):
        print(self.n**2)

obj = Square()
obj.getNum()
obj.printNum()