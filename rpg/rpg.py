import pygame
from pygame.locals import *
import sys
import os

SCR_RECT = Rect(0, 0, 640, 480)
ROW,COL = 15, 20
GS = 32
map = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

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

def draw_map(screen):
    for r in range(ROW):
        for c in range(COL):
            if map[r][c] == 0:
                screen.blit(grassImg, (c * GS, r * GS))
            elif map[r][c] == 1:
                screen.blit(waterImg, (c * GS, r * GS))

# def main():
pygame.init()
screen = pygame.display.set_mode(SCR_RECT.size)
pygame.display.set_caption("RPG")

playerImg = load_image("player1.png", -1)
grassImg = load_image("grass.png")
waterImg = load_image("water.png")

while True:
    draw_map(screen)
    screen.blit(playerImg, (0, 0))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

# if __name__ == '__main__':
#     main()