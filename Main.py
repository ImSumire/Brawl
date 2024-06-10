import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

__inspiration__ = (
    ''
)

__effects__ = (
    'https://github.com/DaFluffyPotato/pygame-shadows',  # nufn
)

__todo__ = (
    "https://youtu.be/OmkAUzvwsDk?si=E2zwbqasMKVCbrkE",
    "https://youtu.be/EHfqrAEmVyg?si=7ePUUqPAlHrdKeeb",
)
import pygame as pg
from pygame import gfxdraw

from Sources.Utils import load, multLoad
from Sources.Button import Button
from Sources.Physics import PhysicsEntity
from Sources.Player import Player
from Sources.Tilemap import Tilemap
from Sources.Camera import Camera

class Game:
    W, H = DIM = 1280, 720
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(self.DIM)
        self.display = pg.Surface((self.W // 3, self.H // 3))

        self.clock = pg.time.Clock()

        self.assets = {
            'grass': multLoad('Tiles/grass'),
            'stone': multLoad('Tiles/stone'),
            'player_stand': load('player.png'),
            'player_fall': load('playerFall.png'),
            'bomb': load('bomb.png'),
            'explosion': load('explosion.png'),
        }

        self.tick = 0

        self.gravity = 0.15
        self.switch = Button(self, 10, 10, 16, 16, self.example)

        self.tilemap = Tilemap(self, tileSize=16)
        self.entities = [
            Player(self, (50, 50), (8, 15)),
            PhysicsEntity(self, "player", (90, 50), (8, 15))
        ]
        self.particules = []
        self.camera = Camera(self.entities[0])

        self.loop()

    def example(self):
        print("Click !")

    def loop(self):
        while True:
            self.events = pg.event.get()
            # Update
            for event in self.events:
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            [entity.update() for entity in self.entities]
            [particule.update() for particule in self.particules]
            self.switch.update()
            self.camera.update()

            # Render
            self.display.fill((0, 0, 0))

            self.tilemap.render()
            [entity.render() for entity in self.entities]
            [particule.render() for particule in self.particules]
            self.switch.render()

            self.screen.blit(pg.transform.scale(self.display, self.DIM), (0, 0))
            pg.display.update()

            self.tick += 1
            self.clock.tick(60)
            pg.display.set_caption(f"Frame per Second : {round(self.clock.get_fps(), 1)}                        Entity count : {len(self.entities)}                        Player pourcentage : {int(self.entities[0].pourcentage * 10)}                        x, y : {int(self.entities[0].x)}, {int(self.entities[0].y)}")

Game()
