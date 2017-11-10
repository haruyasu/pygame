import pygame
from pygame.locals import *
import sys

def calc_ball(ball_x, ball_y, ball_vx, ball_vy, bar1_x, bar1_y, bar2_x, bar2_y):
    if ball_x <= bar1_x + 10.0:
        if ball_y >= bar1_y - 7.5 and ball_y <= bar1_y + 42.5:
            ball_x = 20.0
            ball_vx = -ball_vx

    if ball_x >= bar2_x - 15:
        if ball_y >= bar2_y - 7.5 and ball_y <= bar2_y + 42.5:
            ball_x = 605.0
            ball_vy = -ball_vx

    if ball_x < 5.0:
        ball_x, ball_y = 320.0, 232.5
    elif ball_x > 620.0:
        ball_x, ball_y = 307.5, 232.5

    if ball_y <= 10.0:
        ball_vy = -ball_vy
        ball_y = 10.0
    elif ball_y >= 457.5:
        ball_vy = -ball_vy
        ball_y = 457.5

    return ball_x, ball_y, ball_vx, ball_vy

def calc_ai(ball_x, ball_y, bar2_x, bar2_y):
    dy = ball_y - bar2_y
    if dy > 80:
        bar2_y += 20
    elif dy > 50:
        bar2_y += 15
    elif dy > 30:
        bar2_y += 12
    elif dy > 10:
        bar2_y += 8
    elif dy < -80:
        bar2_y -= 20
    elif dy < -50:
        bar2_y -= 15
    elif dy < -30:
        bar2_y -= 12
    elif dy < -10:
        bar2_y -= 8

    if bar2_y >= 420:
        bar2_y = 420.0
    elif bar2_y <= 10.0:
        bar2_y = 10.0

    return bar2_y

def calc_player(bar1_y, bar1_dy):
    bar1_y += bar1_dy
    if bar1_y >= 420.0:
        bar1_y = 420.0
    elif bar1_y <= 10.0:
        bar1_y = 10.0

    return bar1_y

def calc_score(ball_x, score1, score2):
    if ball_x < 5.0:
        score2 += 1

    if ball_x > 620.0:
        score1 += 1

    return score1, score2

def event(bar1_dy):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_UP:
                bar1_dy = -10
            elif event.key == K_DOWN:
                bar1_dy = 10
        elif event.type == KEYUP:
            if event.key == K_UP:
                bar1_dy = 0.0
            elif event.key == K_DOWN:
                bar1_dy = 0.0

    return bar1_dy

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
        bar1_y = calc_player(bar1_y, bar1_dy)
        time_passed = clock.tick(30)
        time_sec = time_passed / 1000.0
        ball_x += ball_vx * time_sec
        ball_y += ball_vy * time_sec
        score1, score2 = calc_score(ball_x, score1, score2)
        bar2_y = calc_ai(ball_x, ball_y, bar2_x, bar2_y)
        ball_x, ball_y, ball_vx, ball_vy = calc_ball(ball_x, ball_y, ball_vx, ball_vy, bar1_x, bar1_y, bar2_x, bar2_y)
        pygame.display.update()

if __name__ == '__main__':
    main()