import os
import pygame as pg

def load(path):
    try:
        image = pg.image.load("Assets/Sprites/" + path).convert()
        image.set_colorkey((0, 0, 0))
        return image
    except:
        print(f"Error while loading {path}")
        return None


def multLoad(path):
    try:
        sprites = []
        for sprite in sorted(os.listdir("Assets/Sprites/" + path)):
            sprites.append(load(path + "/" + sprite))
        return sprites
    except:
        print(f"Error while loading {path}")
        return []


def gradient(start, end, delta):
    delta = max(1, min(100, delta))

    r1, g1, b1 = start
    r2, g2, b2 = end

    r = int(r1 + (r2 - r1) * (delta * 0.01))
    g = int(g1 + (g2 - g1) * (delta * 0.01))
    b = int(b1 + (b2 - b1) * (delta * 0.01))

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return r, g, b


def scale(image, prod):
    return pg.transform.scale(
        image, (image.get_width() * prod, image.get_height() * prod)
    )

def transition(start: float, end: float, delta: float):
    return start + (end - start) * max(0, min(1, delta))
