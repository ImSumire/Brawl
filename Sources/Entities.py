from math import sqrt, pow, sin, cos
from random import uniform as rand
import numpy as np
import pygame as pg

from Sources.Physics import PhysicsEntity, PhysicsParticule
from Sources.Particule import Particule


class Bomb(PhysicsEntity):
    def __init__(
        self,
        game,
        pos,
        size=(6, 6),
        velocity=(0, 0),
        friction=0.6,
        boucing=0.8,
        trower=None,
    ):
        super().__init__(game, "bomb", pos, size, velocity, friction, boucing)
        self.trower = trower
        self.t = 150

    def update(self):
        super().update()

        self.t -= 1
        if self.t < 0:
            self.game.entities.remove(self)
            self.game.particules.append(
                Particule(self.game, "explosion", (self.dx, self.dy - 5), 5)
            )
            self.game.camera.shakeCool = 10

            for _ in range(20):
                self.game.entities.append(
                    PhysicsParticule(
                        self.game,
                        (self.x + rand(-2, 2), self.y + rand(-2, 2)),
                        (95, 205, 228),
                    )
                )

            for entity in self.game.entities:
                if entity is not self:
                    dist = sqrt(pow(entity.x - self.x, 2) + pow(entity.y - self.y, 2))
                    if dist == 0:
                        dist = 1
                    if dist < 50:
                        if entity.type in ["bomb", "player", "physicsparticule"]:
                            multiplier = 2.5 + self.trower.pourcentage
                            entity.vx += ((entity.x - self.x) / dist) * multiplier
                            entity.vy += ((entity.y - self.y) / dist) * multiplier
                        if entity.type == "player":
                            damage = 50 - dist
                            entity.stuntCool = damage
                            if self.trower is not entity:
                                try:
                                    self.trower.pourcentage += damage * 0.02
                                except:
                                    pass


# class Point(PhysicsEntity):
#     def __init__(self, game, pos, velocity=..., friction=0.2, boucing=0):
#         super().__init__(game, "ropePoint", pos, (1, 1), velocity, friction, boucing)


class Point(PhysicsEntity):
    def __init__(self, game, pos, velocity=(0, 0), locked=False):
        super().__init__(game, "ropePoint", pos, (1, 1), velocity, 0.2, 0)
        self.locked = locked
    
    def update(self):
        # self.vy = min(2.5, max(-2.5, self.vy))
        super().update()

    def render(self, surf):
        pg.draw.circle(
            surf,
            (255, 255, 255) if not self.locked else (255, 0, 0),
            (self.dx, self.dy),
            2,
        )


class Link:
    def __init__(self, a: Point, b: Point, len=None):
        self.a, self.b = a, b
        dx = self.a.x - self.b.x
        dy = self.a.y - self.b.y
        self.len = len or sqrt(dx * dx + dy * dy)

    def update(self):
        dx = self.a.x - self.b.x
        dy = self.a.y - self.b.y
        center = ((self.a.x + self.b.x) * 0.5, (self.a.y + self.b.y) * 0.5)
        if not self.a.locked:
            self.a.x, self.a.y = center
        if not self.b.locked:
            self.b.x, self.b.y = center
        
        dist = sqrt(dx * dx + dy * dy)
        if dist > self.len:
            self.a.x -= dx * 0.35
            self.a.y -= dy * 0.35
            self.b.x += dx * 0.35
            self.b.y += dy * 0.35

    def render(self, surf):
        pg.draw.line(
            surf, (255, 255, 255), (self.a.dx, self.a.dy), (self.b.dx, self.b.dy)
        )


class Hook(PhysicsEntity):
    def __init__(
        self,
        game,
        pos,
        size=(1, 1),
        velocity=(0, 0),
        friction=0.6,
        boucing=0.8,
        trower=None,
        maxLen=150,
    ):
        super().__init__(game, "hook", pos, size, velocity, friction, boucing)
        self.trower = trower
        self.hooked = False
        self.maxLen = maxLen

        self.distPerPoints = 15

        self.points = [Point(self.trower.game, (self.trower.x, self.trower.y))]
        self.links = []
        for _ in range(int(maxLen / self.distPerPoints)):
            self.points.append(Point(self.game, (self.trower.x, self.trower.y)))
            self.links.append(
                Link(self.points[-2], self.points[-1], len=maxLen / self.distPerPoints)
            )
        self.points.append(
            Point(self.trower.game, (self.x, self.y), (self.vx, self.vy))
        )
        self.links.append(
            Link(self.points[-2], self.points[-1], len=maxLen / self.distPerPoints)
        )

    def update(self):
        super().update()
        if not self.hooked and any(self.collisions.values()):
            self.hooked = True

        # Hook anchor
        self.points[-1].x = self.x
        self.points[-1].y = self.y

        if self.hooked:
            # Player anchor
            # self.points[0].x = self.trower.x
            # self.points[0].y = self.trower.y

            self.vx = 0
            self.vy = 0

        for l in self.links:
            l.update()

        for p in self.points:
            p.update()

    def render(self):
        # Hook anchor
        self.points[-1].dx = self.dx
        self.points[-1].dy = self.dy
        
        for p in self.points:
            p.render(self.game.display)
        for l in self.links:
            l.render(self.game.display)
