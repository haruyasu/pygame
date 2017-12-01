import pygame
from pygame.locals import *
import sys
import os

SCR_RECT = Rect(0, 0, 640, 480)
GS = 32
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("RPG")
    Map.images[0] = load_image("grass.png")
    Map.images[1] = load_image("water.png")
    map = Map("test")
    player = Player("player", (1, 1), DOWN)
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        player.update()
        map.draw(screen)
        player.draw(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_DOWN:
                player.move(DOWN, map)

            if event.type == KEYDOWN and event.key == K_LEFT:
                player.move(LEFT, map)

            if event.type == KEYDOWN and event.key == K_RIGHT:
                player.move(RIGHT, map)

            if event.type == KEYDOWN and event.key == K_UP:
                player.move(UP, map)

def load_image(filename, colorkey=None):
    filename = os.path.join("data", filename)

    try:
        image = pygame.image.load(filename)
    except pygame.error, message:
        print "Cannot load image:", filename
        raise SystemExit, message

    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image

def split_image(image):
    imageList = []

    for i in range(0, 128, GS):
        for j in range(0, 128, GS):
            surface = pygame.Surface((GS, GS))
            surface.blit(image, (0, 0), (j, i, GS, GS))
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            surface.convert()
            imageList.append(surface)

    return imageList

class Map:
    images = [None] * 256
    def __init__(self, name):
        self.name = name
        self.row = -1
        self.col = -1
        self.map = []
        self.load()

    def draw(self, screen):
        for r in range(self.row):
            for c in range(self.col):
                screen.blit(self.images[self.map[r][c]], (c * GS, r * GS))

    def is_movable(self, x, y):
        if x < 0 or x > self.col - 1 or y < 0 or y > self.row - 1:
            return False

        if self.map[y][x] == 1:
            return False

        return True

    def load(self):
        file = os.path.join("data", self.name + ".map")
        fp = open(file)
        lines = fp.readlines()
        row_str, col_str = lines[0].split()
        self.row, self.col = int(row_str), int(col_str)
        for line in lines[1:]:
            line = line.rstrip()
            self.map.append([int(x) for x in list(line)])
        fp.close()

class Player:
    animcycle = 24
    frame = 0

    def __init__(self, name, pos, dir):
        self.name = name
        self.images = split_image(load_image("%s.png" % name))
        self.image = self.images[0]
        self.x, self.y = pos[0], pos[1]
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))
        self.direction = dir

    def update(self):
        self.frame += 1
        self.image = self.images[self.direction * 4 + self.frame / self.animcycle % 4]

    def move(self, dir, map):
        if dir == DOWN:
            self.direction = DOWN
            if map.is_movable(self.x, self.y + 1):
                self.y += 1
                self.rect.top += GS
        elif dir == LEFT:
            self.direction = LEFT
            if map.is_movable(self.x - 1, self.y):
                self.x -= 1
                self.rect.left -= GS
        elif dir == RIGHT:
            self.direction = RIGHT
            if map.is_movable(self.x + 1, self.y):
                self.x += 1
                self.rect.left += GS
        elif dir == UP:
            self.direction = UP
            if map.is_movable(self.x, self.y - 1):
                self.y -= 1
                self.rect.top -= GS

    def draw(self, screen):
        screen.blit(self.image, self.rect)

if __name__ == '__main__':
    main()
