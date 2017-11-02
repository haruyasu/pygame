import pygame
from pygame.locals import *
import math, sys
import pygame.mixer

SCREEN = Rect(0, 0, 400, 400)

class Paddle(pygame.sprite.Sprite):
    def __init__(self, filename):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN.bottom - 20

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.clamp_ip(SCREEN)

class Ball(pygame.sprite.Sprite):
    speed = 5
    angle_left = 135
    angle_right = 45

    def __init__(self, filename, paddle, blocks, score):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.dx = self.dy = 0
        self.paddle = paddle
        self.blocks = blocks
        self.update = self.start
        self.score = score
        self.hit = 0

    def start(self):
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top

        if pygame.mouse.get_pressed()[0] == 1:
            self.dx = 0
            self.dy = -self.speed
            self.update = self.move

class Block(pygame.sprite.Sprite):
    def __init__(self, filename, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.rect.left = SCREEN.left + x * self.rect.width
        self.rect.top = SCREEN.top + y * self.rect.height

class Score():
    def __init__(self, x, y):
        self.sysfont = pygame.font.SysFont(None, 20)
        self.score = 0

    def draw(self, screen):
        img = self.sysfont.render("SCORE:" + str(self.score), True, (255, 255, 250))
        screen.blit(img, (self.x, self.y))

    def add_score(self, x):
        self.score += x

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    Ball.paddle_sound = pygame.mixer.Sound("flashing.mp3")
    Ball.block_sound = pygame.mixer.Sound("flying_pan.mp3")
    Ball.gameover_sound = pygame.mixer.Sound("badend1.mp3")
    group = pygame.sprite.RenderUpdates()
    blocks = pygame.sprite.Group()
    Paddle.containers = group
    Ball.containers = group
    Block.containers = group, blocks
    paddle = Paddle("paddle.png")

    for x in range(1, 15):
        for y in range(1, 11):
            Block("block.png", x, y)

    score = Score(10, 10)
    Ball("ball.png", paddle, blocks, score)
    clock = pygame.time.Clock()



if __name__ == '__main__':
    main()