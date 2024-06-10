class Particule:
    def __init__(self, game, pType, pos, lifetime):
        self.game = game
        self.type = pType
        self.x, self.y = pos
        self.t = lifetime

    def update(self):
        self.t -= 1
        if self.t < 0:
            self.game.particules.remove(self)

    def render(self):
        self.game.display.blit(self.game.assets[self.type], (self.x, self.y))
