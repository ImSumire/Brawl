import pygame
from pygame.locals import *
import math
from random import choice


W = 1280
H = 720

ACC_X = 0  # global x acceleration
ACC_Y = 500  # global y acceleration

BALLOON_ACC_X = 0
BALLOON_ACC_Y = -250

USE_STRESS = True
MAX_STRESS = 15
MAX_STRESS_FACTOR = 1 / MAX_STRESS

GRID_SIZE = 25  # size (in pixels) of the snapping grid
SNAP_RADIUS = 20  # within this distance, a stick will snap to the nearest node while being created
DELETE_RADIUS = 10

NODE_RADIUS = 4
BALLOON_RADIUS = 15
STICK_WIDTH = 7

WHITE = (255, 255, 255)
BG = (65, 65, 130)
NODE_PREVIEW_COLOR = (85, 85, 160)
NODE_COLOR = (255, 255, 255)
BALLOON_COLOR = (161, 27, 191)
LOCKED_NODE_COLOR = (255, 75, 75)
DELETING_COLOR = (255, 105, 105)


class Node:
    def __init__(self, pos, locked=False, isNew=True, mass=1):
        self.pos = pos
        self.prev = pos
        self.locked = locked
        self.isNew = isNew  # don't apply physics to it
        self.sticks = []
        self.mass = mass

    def update(self, dt):
        posBeforeUpdate = self.pos
        self.pos = (2 * self.pos[0] - self.prev[0], 2 * self.pos[1] - self.prev[1])
        self.pos = (
            self.pos[0] + ACC_X * (dt * dt),
            self.pos[1] + ACC_Y * (dt * dt) * self.mass,
        )
        self.prev = posBeforeUpdate

        if self.pos[1] > H - NODE_RADIUS:  # bounce off bottom
            excess = self.pos[1] - (H - NODE_RADIUS)
            self.prev = (
                self.prev[0],
                self.pos[1] + 0.5 * (self.pos[1] - self.prev[1]) - excess,
            )
            self.pos = (self.pos[0], H - NODE_RADIUS)


class Balloon(Node):
    def __init__(self, pos):
        super().__init__(pos)
        self.isNew = False

    def update(self, dt):
        posBeforeUpdate = self.pos
        self.pos = (2 * self.pos[0] - self.prev[0], 2 * self.pos[1] - self.prev[1])
        self.pos = (
            self.pos[0] + BALLOON_ACC_X * (dt * dt),
            self.pos[1] + BALLOON_ACC_Y * (dt * dt) * self.mass,
        )
        self.prev = posBeforeUpdate

        if self.pos[1] > H - BALLOON_RADIUS:  # bounce off bottom
            excess = self.pos[1] - (H - BALLOON_RADIUS)
            self.prev = (
                self.prev[0],
                self.pos[1] + 0.5 * (self.pos[1] - self.prev[1]) - excess,
            )
            self.pos = (self.pos[0], H - BALLOON_RADIUS)


class Stick:
    def __init__(self, a: Node, b: Node, game):
        self.game = game
        self.a = a
        self.b = b
        self.len = dist(self.a.pos, self.b.pos)
        a.sticks.append(self)
        b.sticks.append(self)

    def getCenter(self):
        return (
            (self.a.pos[0] + self.b.pos[0]) * 0.5,
            (self.a.pos[1] + self.b.pos[1]) * 0.5,
        )

    def getStress(self):
        return dist(self.a.pos, self.b.pos) - self.len

    def getStressColor(self):
        return (
            min(max(30 + self.getStress() * 225 * MAX_STRESS_FACTOR, 0), 255),
            min(max(120 - self.getStress() * 8, 0), 255),
            50,
        )

    def getNodes(self):
        return [self.a, self.b]


class Game:
    def __init__(self, nodes=[], sticks=[]):
        self.nodes: list = nodes
        self.sticks: list = sticks

    def update(self, d_time):
        d_time = max(d_time, 0.01)
        for node in self.nodes:
            if not node.locked and not node.isNew:
                node.update(d_time)

        for stick in self.sticks:
            if USE_STRESS and stick.getStress() > MAX_STRESS:
                self.sticks.remove(stick)
            stick_center = stick.getCenter()
            distance = dist(stick.a.pos, stick.b.pos)
            stick_dir = (
                (stick.a.pos[0] - stick.b.pos[0]) / distance,
                (stick.a.pos[1] - stick.b.pos[1]) / distance,
            )
            if not stick.a.locked:
                stick.a.pos = (
                    stick_center[0] + stick_dir[0] * stick.len / 2,
                    stick_center[1] + stick_dir[1] * stick.len / 2,
                )
            if not stick.b.locked:
                stick.b.pos = (
                    stick_center[0] - stick_dir[0] * stick.len / 2,
                    stick_center[1] - stick_dir[1] * stick.len / 2,
                )

    def create_fabric(self, pos, width, height, space_between):
        grid = [
            [
                Node(
                    (pos[0] + x * space_between, pos[1] + y * space_between),
                    False,
                    False,
                )
                for x in range(width)
            ]
            for y in range(height)
        ]
        for row in grid:
            for node in row:
                self.nodes.append(node)
        for y in range(height):
            for x in range(width - 1):
                self.sticks.append(Stick(grid[y][x], grid[y][x + 1], self))
        for y in range(height - 1):
            for x in range(width):
                self.sticks.append(Stick(grid[y][x], grid[y + 1][x], self))


def dist(pos1, pos2):
    return max(math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]), 0.001)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ropes")
    clock = pygame.time.Clock()
    game = Game()

    game.create_fabric((200, 200), 17, 15, 20)

    paused = True
    masses = [1, 10, -1]
    mi = 0
    while True:
        clock.tick(60)

        mousePos = pygame.mouse.get_pos()  # get mouse position
        placePos = mousePos
        # if there is a node nearby, start drawing at that node; otherwise, create a new node
        nearest = None
        distNearest = SNAP_RADIUS
        for node in game.nodes:
            distance = dist(mousePos, node.pos)
            if distance < distNearest:
                nearest = node
                distNearest = distance

        drawing = False
        deleting = False

        # process inputs
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused
                if event.key == K_b:
                    balloon = Balloon(placePos)
                    game.nodes.append(balloon)
                if event.key == K_h:
                    mi = (mi + 1) % 3
                    print(masses[mi])
                if event.key == K_d:
                    game.sticks = []
                    game.nodes = []
                    paused = True

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if nearest:
                    nodeA = nearest
                else:
                    nodeA = Node(placePos, mass=masses[mi])
                    game.nodes.append(nodeA)

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if nearest:
                    nodeB = nearest
                else:
                    nodeB = Node(placePos)
                    game.nodes.append(nodeB)

                if nodeA != nodeB:
                    if not any([nodeB in stick.getNodes() for stick in nodeA.sticks]):
                        game.sticks.append(Stick(nodeA, nodeB, game))
                elif not nodeA.isNew and not isinstance(nodeA, Balloon):
                    nodeA.locked = not nodeA.locked

                nodeA.isNew = False
                nodeB.isNew = False

        if pygame.mouse.get_pressed()[
            0
        ]:  # left mouse is being held, preview stick placement
            drawing = True

        if (
            not drawing and pygame.mouse.get_pressed()[2]
        ):  # if right mouse button is being held, remove any object hovered near
            deleting = True
            if nearest:
                game.nodes.remove(nearest)
                for stick in nearest.sticks:
                    try:
                        game.sticks.remove(stick)
                    except Exception:
                        pass
            for stick in game.sticks:
                if dist(mousePos, stick.getCenter()) < DELETE_RADIUS + STICK_WIDTH:
                    game.sticks.remove(stick)

        for node in game.nodes:
            if node.pos[1] > W + H:  # node is far below screen; delete it
                game.nodes.remove(node)
                for stick in node.sticks:
                    try:
                        game.sticks.remove(stick)
                    except Exception:
                        pass

        if not paused:
            game.update(clock.tick() / 1000)

        # Visuals
        screen.fill(BG)

        if deleting:
            pygame.draw.circle(screen, DELETING_COLOR, mousePos, DELETE_RADIUS)

        if drawing:
            pygame.draw.line(
                screen,
                NODE_PREVIEW_COLOR,
                nodeA.pos,
                nearest.pos if nearest else placePos,
                STICK_WIDTH,
            )

        pygame.draw.circle(
            screen,
            NODE_PREVIEW_COLOR,
            nearest.pos if nearest else placePos,
            NODE_RADIUS,
        )  # mouse cursor thingy

        for stick in game.sticks:
            pygame.draw.line(
                screen, stick.getStressColor(), stick.a.pos, stick.b.pos, STICK_WIDTH
            )
        for node in game.nodes:
            pygame.draw.circle(
                screen,
                BALLOON_COLOR
                if isinstance(node, Balloon)
                else (
                    LOCKED_NODE_COLOR
                    if node.locked
                    else (
                        NODE_COLOR
                        if node.mass == 1
                        else ((255, 100, 255) if node.mass == 10 else (100, 100, 255))
                    )
                ),
                node.pos,
                BALLOON_RADIUS if isinstance(node, Balloon) else NODE_RADIUS,
            )

        if paused:
            pygame.draw.rect(screen, WHITE, Rect(20, 20, 7, 25))
            pygame.draw.rect(screen, NODE_COLOR, Rect(33, 20, 7, 25))

        pygame.display.flip()

        pygame.display.set_caption(f"FPS: {int(clock.get_fps())}")


if __name__ == "__main__":
    main()
