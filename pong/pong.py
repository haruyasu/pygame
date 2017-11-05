import pygame
from pygame.locals import *
import sys

def event(bar1_dy):
    pass

def main():
    bar1_x, bar1_y = 10.0 , 215.0
    bar2_x, bar2_y = 620.0 , 215.0
    ball_x, ball_y = 307.5 , 232.5
    bar1_dy, bar2_dy = 0.0 , 0.0
    ball_vx, ball_vy = 250.0 , 250.0
    score1, score2 = 0, 0
    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0, 32)
    pygame.display.set_caption("PONG")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    back = pygame.Surface((640, 480))
    background = back.convert()
    screen.fill((0, 0, 0))
    bar = pygame.Surface((10, 50))
    bar1 = bar.convert()
    bar1.fill((255, 255, 255))
    bar2 = bar.convert()
    bar2.fill((255, 255, 255))
    circ_sur = pygame.Surface((20, 20))
    pygame.draw.circle(circ_sur, (255, 255, 255), (15 / 2, 15 / 2), 15 / 2)
    ball = circ_sur
    ball.set_colorkey((0, 0, 0))

    while (1):
        screen.blit(background, (0, 0))
        pygame.draw.aaline(screen, (255, 255, 255), (330, 5), (330, 475))
        screen.blit(bar1, (bar1_x, bar1_y))
        screen.blit(bar2, (bar2_x, bar2_y))
        screen.blit(ball, (ball_x, ball_y))
        screen.blit(font.render(str(score1), True, (255, 255, 255)), (255.0, 10.0))
        screen.blit(font.render(str(score2), True, (255, 255, 255)), (400.0, 10.0))
        bar1_dy = event(bar1_dy)



if __name__ == '__main__':
    main()