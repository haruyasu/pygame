import pygame
from pygame.locals import *
import math, sys
import pygame.mixer

SCREEN = Rect(0, 0, 400, 400)

class Ball(pygame.sprite.Sprite):
    speed = 5
    angle_left = 135
    angle_right = 45

    def __init__(self, filename, paddle, blocks, score):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get.roct()
        self.dx = self.dy = 0
        self.paddle = paddle
        self.blocks = blocks
        self.update = self.start
        self.score = score
        self.hit = 0



def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    # Ball.paddle_sound = pygame.mixer.Sound("flashing.mp3")


if __name__ == '__main__':
    main()