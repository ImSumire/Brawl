from random import randint as rand

class Camera:
    def __init__(self, target):
        self.target = target
        self.xOff = self.target.game.W // 9
        self.yOff = self.target.game.H // 6
        self.x, self.y = -self.xOff, -self.yOff

        self.shakeCool = 0

    def update(self):
        self.x += (self.target.x - self.x - self.xOff) / 20
        self.y += (self.target.y - self.y - self.yOff) / 20

        self.shakeCool -= 1
        if self.shakeCool > 0:
            self.x += rand(-2, 2)
            self.y += rand(-2, 2)