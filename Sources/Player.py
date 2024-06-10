import numpy as np
import pygame as pg

from Sources.Physics import PhysicsEntity
from Sources.Entities import Bomb, Hook

class Player(PhysicsEntity):
    def __init__(self, game, pos, size, velocity=(0, 0), friction=0.2, boucing=0):
        super().__init__(game, "player", pos, size, velocity)

        self.pourcentage = 0.0

        self.aimVect = np.empty(2)

        self.trowCool = 0
        self.wallJumpCool = 0
        self.dashCool = 0
        self.stuntCool = 0

        self.doubleJump = False
        self.grapingTrowed = False
        self.grapingLen = 200

        self.graping = None

    def update(self):
        keys = pg.key.get_pressed()
        self.left = self.right = self.jump = False

        if self.stuntCool < 0:
            if keys[pg.K_d]:
                self.right = True
                self.flip = False
            elif keys[pg.K_q]:
                self.left = True
                self.flip = True
            if keys[pg.K_SPACE]:
                self.jump = True
            if pg.K_e in [e.key for e in self.game.events if e.type == pg.KEYDOWN]:
                if not self.grapingTrowed:
                    self.grapingTrowed = True
                    self.hook = Hook(
                        self.game,
                        (self.x, self.y),
                        size=(1, 1),
                        velocity=self.aimVect * 0.12,
                        trower=self
                    )
                    self.game.entities.append(self.hook)
                else:
                    self.grapingTrowed = False
                    self.game.entities.remove(self.hook)
                    self.hook = None
                    self.grapingLen = 200
            if keys[pg.K_DOWN]:
                if self.grapingTrowed and self.hook.hooked:
                    self.grapingLen -= 0.5
            if keys[pg.K_LCTRL]:
                if self.dashCool < 0:
                    self.dashCool = 150
                    self.vx += (-3, 3)[self.aimVect[0] > 0]
            if keys[pg.K_a]:
                if self.trowCool < 0:
                    self.trowCool = 10
                    self.game.entities.append(
                        Bomb(
                            self.game,
                            (self.x, self.y),
                            velocity=self.aimVect * 0.06,
                            trower=self
                        )
                    )

        super().update()

        if self.jump:
            # Normal jump
            if self.collisions["down"]:
                self.vy -= 4
                self.wallJumpCool = 0
                self.doubleJump = True
            # Left wall jump
            elif self.collisions["right"] and self.wallJumpCool < 0 and self.vy > 0:
                self.vy -= 4
                self.vx -= 1
                self.wallJumpCool = 200
            # Right wall jump
            elif self.collisions["left"] and self.wallJumpCool < 0 and self.vy > 0:
                self.vy -= 4
                self.vx += 1
                self.wallJumpCool = 200
            # Air jump (aka double jump)
            elif self.doubleJump and self.vy > 0:
                self.vy = -4
                self.doubleJump = False

        self.wallJumpCool -= 1
        self.trowCool -= 1
        self.dashCool -= 1
        self.stuntCool -= 1

        if self.y > 500:
            self.y = 50
            self.x = 50
            self.pourcentage = 0.0

        if self.collisions["down"]:
            self.airTime = 0

        if self.airTime > 4:
            self.action = "fall"

        # elif self.vx != 0 and self.collisions["down"]:
        #     self.set_action("run")
        
        else:
            self.action = "stand"

    def render(self):
        self.aimVect = pg.mouse.get_pos()
        self.aimVect = np.array(pg.mouse.get_pos(), dtype=np.float64) // 3 - np.array((self.dx, self.dy), dtype=np.float64)
        if self.aimVect[0] or self.aimVect[1]:
            dist = np.linalg.norm(self.aimVect)
            self.aimVect /= dist
            self.aimVect *= min(100, dist)
        lineVect = self.aimVect + np.array((self.dx, self.dy), dtype=np.float64)
        pg.draw.line(
            self.game.display,
            (100, 100, 100),
            (self.dx + self.w // 2, self.dy + self.h // 2), 
            (int(lineVect[0]), int(lineVect[1]))
        )
        super().render()
