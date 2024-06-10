import pygame as pg


NEIGHBORS = [
    (-1,  1), ( 0,  1), ( 1,  1),
    (-1,  0), ( 0,  0), ( 1,  0),
    (-1, -1), ( 0, -1), ( 1, -1),
]
PHYSICS_TILES = {"grass", "stone"}


class Tilemap:
    def __init__(self, game, tileSize=16):
        self.game = game
        self.tileSize = tileSize
        self.tilemap = {}
        self.offgridTiles = []

        for i in range(20):
            x, y = -7 + i, 10
            self.tilemap[f"{x};{y}"] = {
                "type": "grass",
                "variant": 1,
                "pos": (x, y),
            }
            x, y = 10, 5 + i
            self.tilemap[f"{x};{y}"] = {
                "type": "stone",
                "variant": 1,
                "pos": (x, y),
            }
            # x, y = 1, 0 + i
            # self.tilemap[f"{x};{y}"] = {
            #     "type": "stone",
            #     "variant": 1,
            #     "pos": (x, y),
            # }
            x, y = 3 + i, 1
            self.tilemap[f"{x};{y}"] = {
                "type": "grass",
                "variant": 1,
                "pos": (x, y),
            }
            x, y = 20 + i, 20
            self.tilemap[f"{x};{y}"] = {
                "type": "grass",
                "variant": 1,
                "pos": (x, y),
            }

    def tilesAround(self, pos):
        tiles = []
        tileLoc = (int(pos[0] // self.tileSize), int(pos[1] // self.tileSize))
        for offset in NEIGHBORS:
            check_loc = (
                str(tileLoc[0] + offset[0]) + ";" + str(tileLoc[1] + offset[1])
            )
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def physicsRectsAround(self, pos):
        rects = []
        for tile in self.tilesAround(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(
                    pg.Rect(
                        tile["pos"][0] * self.tileSize,
                        tile["pos"][1] * self.tileSize,
                        self.tileSize,
                        self.tileSize,
                    )
                )
        return rects

    def render(self):
        surf = self.game.display
        ox, oy = int(self.game.camera.x), int(self.game.camera.y)
        
        for tile in self.offgridTiles:
            surf.blit(
                self.game.assets[tile["type"]][tile["variant"]],
                (tile["pos"][0] - ox, tile["pos"][1] - oy),
            )

        for x in range(
            ox // self.tileSize,
            (ox + surf.get_width()) // self.tileSize + 1,
        ):
            for y in range(
                oy // self.tileSize,
                (oy + surf.get_height()) // self.tileSize + 1,
            ):
                loc = str(x) + ";" + str(y)
                try:
                    tile = self.tilemap[loc]
                    surf.blit(
                        self.game.assets[tile["type"]][tile["variant"]],
                        (
                            tile["pos"][0] * self.tileSize - ox,
                            tile["pos"][1] * self.tileSize - oy,
                        ),
                    )
                except:
                    pass
