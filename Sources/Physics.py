import numpy as np
import pygame as pg
from pygame import gfxdraw

from Sources.Particule import Particule


class PhysicsEntity:
    def __init__(self, game, eType, pos, size, velocity=(0, 0), friction=0.2, boucing=0):
        self.game = game

        self.type = eType

        self.x, self.y = pos
        self.w, self.h = size
        self.vx, self.vy = velocity
        self.dx, self.dy = 0, 0
        self.mass = 1

        self.friction = friction
        self.bouncing = boucing

        self.left = self.right = self.jump = False

        self.airTime = 0

        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        self.action = "stand"
        # self.anim_offset = (-3, -3)
        self.flip = False
        # self.set_action("idle")

    def rect(self):
        return pg.Rect(self.x, self.y, self.w, self.h)

    # def set_action(self, action):
    #     if action != self.action:
    #         self.action = action
    #         self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def update(self):
        self.collisions = {"up": False, "down": False, "right": False, "left": False}

        tilemap = self.game.tilemap

        self.x += self.vx
        entityRect = self.rect()
        for rect in tilemap.physicsRectsAround((self.x, self.y)):
            if entityRect.colliderect(rect):
                if self.vx > 0:
                    entityRect.right = rect.left
                    self.collisions["right"] = True
                    self.vx = round(-self.vx * self.bouncing, 2)
                    # self.vx = min(self.vx, 0)
                elif self.vx < 0:
                    entityRect.left = rect.right
                    self.collisions["left"] = True
                    self.vx = round(-self.vx * self.bouncing, 2)
                    # self.vx = max(self.vx, 0)
                else:
                    self.vx *= 0.9  # Air friction
                self.x = entityRect.x

        self.y += self.vy
        entityRect = self.rect()
        for rect in tilemap.physicsRectsAround((self.x, self.y)):
            if entityRect.colliderect(rect):
                if self.vy > 0:
                    entityRect.bottom = rect.top
                    self.collisions["down"] = True
                    self.vx *= self.friction
                    self.vy = int(-self.vy * self.bouncing)
                    self.doubleJump = True
                elif self.vy < 0:
                    entityRect.top = rect.bottom
                    self.collisions["up"] = True
                    self.vy = 0
                self.y = entityRect.y

        dir = (self.right - self.left) * 2
        if (self.vx > -1.5 and dir < 0) or (self.vx < 1.5 and dir > 0):
            # Limits air motion to avoid adding too much velocity
            self.vx += dir * (1 if self.collisions["down"] else 0.3)

        self.vy += self.game.gravity * self.mass

        # Clamping
        self.vy = min(5, max(-5, self.vy))

        self.airTime += 1
        
        self.dx = int(self.x) - int(self.game.camera.x)
        self.dy = int(self.y) - int(self.game.camera.y)

        # self.animation.update()

    def render(self):
        try:
            sprite = self.game.assets[f"{self.type}_{self.action}"]
        except:
            sprite = self.game.assets[f"{self.type}"]

        self.game.display.blit(
            pg.transform.flip(
                sprite,
                self.flip,
                False
            ),
            (self.dx, self.dy),
        )

class PhysicsParticule(PhysicsEntity):
    def __init__(self, game, pos, color, velocity=(0, 0), lifetime=60):
        super().__init__(game, "physicsparticule", pos, (1, 1), velocity, boucing=0.4)
        self.color = color
        self.t = lifetime

    def update(self):
        super().update()
        self.vy -= self.game.gravity / 2
        self.t -= 1
        if self.t < 0:
            self.game.entities.remove(self)

    def render(self):
        gfxdraw.box(
            self.game.display,
            (self.dx, self.dy, 1, 1),
            (*self.color, min(255, self.t * 15))
        )
