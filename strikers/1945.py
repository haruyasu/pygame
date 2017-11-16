import pygame
from pygame.locals import *
import os, math, random, sys

SCR_RECT = Rect(0, 0, 640, 480)
PLAY_MENU, QUIT_MENU = (0, 1)
TITLE, PLAY, GAMEOVER = (0, 1, 2)

class main():
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("Strikers1945")
        self.load_images()
        self.load_sounds()
        self.init_game()
        clock = pygame.time.Clock()

    def init_game(self):
        pass

    def load_images(self):
        pass

    def load_sounds(self):
        pass

def image_colorkey(image, colorkey):
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_image(filename, colorkey=None):
    filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename).convert()
    except pygame.error, message:
        print "Cannot load image:", filename
        raise SystemExit, message
    return image_colorkey(image, colorkey)

def load_sound(filename):
    filename = os.path.join("data", filename)
    return pygame.mixer.Sound(filename)

if __name__ == '__main__':
    main()