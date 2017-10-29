import pygame, time

black = (0, 0, 0)
white = (255, 255, 255)

pygame.init()

surfaceWidth = 800
surfaceHeight = 500

surface = pygame.display.set_mode((surfaceWidth, surfaceHeight))
pygame.display.set_caption('Helicopter')
clock = pygame.time.Clock()
img = pygame.image.load('Helicopter.png')

def replay_or_quit():
    for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT]):
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            continue

        return event.key
    return None

def makeTextObjs(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()

def msgSurface(text):
    smallText = pygame.font.Font('freesansbold.ttf', 20)
    largeText = pygame.font.Font('freesansbold.ttf', 150)

    titleTextSurf, titleTextRect = makeTextObjs(text, largeText)
    titleTextRect.center = surfaceWidth / 2, surfaceHeight / 2
    surface.blit(titleTextSurf, titleTextRect)

    typeTextSurf, typeTextRect = makeTextObjs('Press any key to continue!', smallText)
    typeTextRect.center = surfaceWidth / 2, ((surfaceHeight / 2) + 100)
    surface.blit(typeTextSurf, typeTextRect)

    pygame.display.update()
    time.sleep(1)

    while replay_or_quit() == None:
        clock.tick()

    main()

def gameOver():
    msgSurface('Crash!!')

def helicopter(x, y, image):
    surface.blit(img, (x, y))

def main():
    x = 150
    y = 200
    y_move = 4
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    y_move = -4

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    y_move = 4

        y += y_move

        surface.fill(black)
        helicopter(x, y, img)

        if y > surfaceHeight - 40 or y < 0:
            gameOver()

        pygame.display.update()
        clock.tick(60)

main()
pygame.quit()
quit()