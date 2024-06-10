import pygame
import numpy as np

class Point:
	def __init__(self, position, radius=5):
		self.pos = position
		self.pos_prev = None
		self.radius = radius
		self.locked = False

	def draw(self, WIN):
		pygame.draw.circle(WIN, (255, 255, 255) if not self.locked else (255, 0, 0), self.pos, self.radius)
	
	def update(self, gravity):		
		if not self.locked:
			pos_before_update = self.pos.copy()
			if self.pos_prev is not None:
				self.pos += self.pos - self.pos_prev
			self.pos[1] += gravity
			self.pos_prev = pos_before_update
	
	def is_clicked(self, pos):
		return np.linalg.norm(pos - self.pos) <= self.radius * 1.5
	
class Stick:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.len = np.linalg.norm(self.a.pos - self.b.pos)
        
    def update(self):
        center = (self.a.pos + self.b.pos) * 0.5
        dir = (self.a.pos - self.b.pos)
        dir = dir / np.linalg.norm(dir)
        if not self.a.locked:
            self.a.pos = center + dir * self.len * 0.5
        if not self.b.locked:
            self.b.pos = center - dir * self.len * 0.5
        
    def draw(self, WIN):
        pygame.draw.line(WIN, (255, 255, 255), self.a.pos, self.b.pos)

# Display
SIZE = (1000, 950)
display = pygame.display.set_mode(SIZE)

# Constants
GRAVITY = 0.16

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def simulate(points, sticks):
	for point in points:
		point.update(GRAVITY)
	
	for stick in sticks:
		stick.update()

def main():
	paused = True

	points = []
	sticks = []

	clock = pygame.time.Clock()
	running = True
	while running:
		display.fill([0, 0, 0])
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			
			if event.type == pygame.MOUSEBUTTONDOWN and paused:
				mouse_pos = np.array(pygame.mouse.get_pos())
				clicked_point = False

				for point in points:
					if point.is_clicked(mouse_pos):
						point.locked = not point.locked
						clicked_point = True

				if not clicked_point:
					points.append(Point(mouse_pos))
					if len(points) > 1:
						sticks.append(Stick(points[-2], points[-1]))
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					paused = not paused

		if not paused:
			simulate(points, sticks)
		
		for stick in sticks:
			stick.draw(display)

		for point in points:
			if paused:
				point.draw(display)
		

		pygame.display.set_caption(f"FPS: {clock.get_fps()}")
		pygame.display.update()
		clock.tick(60)
		
	pygame.quit()


if __name__ == '__main__':
	main()
