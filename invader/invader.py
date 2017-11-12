import pygame
from pygame.locals import *
import os, random, sys

START, PLAY, GAMEOVER = (0, 1, 2)
SCR_RECT = Rect(0, 0, 640, 480)

class main():
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("Game Over")
        self.load_images()
        self.load_sounds()
        self.init_game()
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()

    def init_game(self):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    def key_handler(self):
        pass

    def collision_detection(self):
        pass

    def load_images(self):
        Player.image = load_image("player.png")
        Shot.image = load_image("shot.png")
        Alien.images = split_image(load_image("alien.png"), 2)
        Beam.image = load_image("beam.png")
        Explosion.images = split_image(load_image("explosion.png"), 16)

    def load_sounds(self):
        Alien.kill_sound = load_sound("kill.wav")
        Player.shot_sound = load_sound("shot.wav")
        Player.bomb_sound = load_sound("bomb.wav")

class Player(pygame.sprite.Sprite):
    pass

class Alien(pygame.sprite.Sprite):
    pass

class Shot(pygame.sprite.Sprite):
    pass

class Beam(pygame.sprite.Sprite):
    pass

class Explosion(pygame.sprite.Sprite):
    pass

def load_image(filename, colorkey=None):
    filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error, message:
        print "Cannot load images: "
        raise SystemExit, message
    image = image.convert()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image

def split_image(image, n):
    image_list = []
    w = image.get_width()
    h = image.get_height()
    w1 = w / n

    for i in range(0, w, w1):
        surface = pygame.Surface((w1, h))
        surface.blit(image, (0, 0), (i, 0, w1, h))
        surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
        surface.convert()
        image_list.append(surface)

    return image_list

def load_sound(filename):
    filename = os.path.join("data", filename)
    return pygame.mixer.Sound(filename)

if __name__ == '__main__':
    main()