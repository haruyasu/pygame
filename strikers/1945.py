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
        self.game_state = TITLE
        self.cur_menu = PLAY_MENU
        self.all = pygame.sprite.RenderUpdates()
        self.shots = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bombs = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.explosion = pygame.sprite.Group()

        Plane.containers = self.all
        Shot.containers = self.shots, self.all
        Enemy.containers = self.enemies, self.obstacles, self.all
        Bomb.containers = self.bombs, self.obstacles, self.all
        Explosion.containers = self.all
        PlaneExplosion.containers = self.all

        self.battlefield = Battlefield()
        self.plane = Plane()
        Bomb.plane = self.plane
        self.score_board = ScoreBoard()

    def load_images(self):
        sprite_sheet = SpriteSheet("1945.png")
        Battlefield.ocean_tile = sprite_sheet.image_at((268,367,32,32))
        Plane.opaque_images = sprite_sheet.images_at([(305,113,61,49), (305,179,61,49), (305,245,61,49)], -1)
        Plane.transparent_images = sprite_sheet.images_at([(305,113,61,49), (305,179,61,49), (305,245,61,49)], -1)

        for image in Plane.transparent_images:
            image.set_alpha(80)

        Shot.image = sprite_sheet.image_at((48,176,9,20), -1)
        Enemy.image_sets = [
            sprite_sheet.images_at([(4,466,32,32), (37,466,32,32), (70,466,32,32)], -1),
            sprite_sheet.images_at([(103,466,32,32), (136,466,32,32), (169,466,32,32)], -1),
            sprite_sheet.images_at([(202,466,32,32), (235,466,32,32), (268,466,32,32)], -1),
            sprite_sheet.images_at([(301,466,32,32), (334,466,32,32), (367,466,32,32)], -1),
            sprite_sheet.images_at([(4,499,32,32), (37,499,32,32), (70,499,32,32)], -1)]
        Bomb.image = sprite_sheet.image_at((278,113,13,13), -1)
        Explosion.images = sprite_sheet.images_at([(70,169,32,32), (103,169,32,32),
            (136,169,32,32), (169,169,32,32), (202,169,32,32), (235,169,32,32)], -1)
        PlaneExplosion.images = sprite_sheet.images_at([(4,301,65,65), (70,301,65,65),
            (136,301,65,65), (202,301,65,65), (268,301,65,65), (334,301,65,65), (400,301,65,65)], -1)
        ScoreBoard.number_images = sprite_sheet.images_at([(580,107,9,12), (590,107,9,12),
            (601,107,9,12), (611,107,9,12), (621,107,9,12), (632,107,9,12),
            (642,107,9,12), (652,107,9,12), (662,107,9,12), (672,107,9,12)], -1)
        ScoreBoard.score_label = sprite_sheet.image_at((574,161,59,12), -1)
        Plane.power_image = sprite_sheet.image_at((202,268,31,31), -1)

        self.title_image = sprite_sheet.image_at((104,578,275,138), -1)
        self.play_game_image = sprite_sheet.image_at((580,389,95,14), -1)
        self.quit_image = sprite_sheet.image_at((580,461,42,14), -1)
        self.cursor_image = sprite_sheet.image_at((569,389,7,12), -1)
        self.gameover_image = sprite_sheet.image_at((303,520,96,12), -1)

    def load_sounds(self):
        Plane.bomb_sound = load_sound("bom28_a.wav")
        Enemy.bomb_sound = load_sound("bom24.wav")
        self.cursor_sound = load_sound("cursor07.wav")
        self.select_sound = load_sound("cursor02.wav")

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