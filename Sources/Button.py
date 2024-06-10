import pygame as pg


class Button:
    def __init__(self, game, x, y, w, h, func):
        self.game = game

        self.x, self.y = x, y
        self.w, self.h = w, h

        self.rect = pg.Rect(self.x, self.y, self.w, self.h)
        self.rect.topleft = self.x, self.y

        self.func = func

        self.pressed = False

    def render(self):
        pg.draw.rect(self.game.display, (255, 255, 255), self.rect)

    def update(self):
        mx, my = pg.mouse.get_pos()
        if self.rect.collidepoint((mx // 3, my // 3)):
            if pg.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed:
                    self.pressed = False
                    self.func()
