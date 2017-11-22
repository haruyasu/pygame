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

        while True:
            clock.tick(60)
            screen.fill((255, 0, 0))
            self.update()
            self.draw(screen)
            pygame.display.update()
            self.key_handler()

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

    def update(self):
        if self.game_state == TITLE:
            self.battlefield.update()
            self.enemies.update()
        elif self.game_state == PLAY:
            self.battlefield.update()
            self.all.update()
            self.collide_detection()
        elif self.game_state == GAMEOVER:
            self.battlefield.update()
            self.enemies.update()

    def draw(self, screen):
        if self.game_state == TITLE:
            screen.blit(self.battlefield.ocean, (0, 0), self.battlefield.offset())
            self.enemies.draw(screen)
            screen.blit(self.title_image, (182, 80))
            screen.blit(self.play_game_image, (280, 300))
            screen.blit(self.quit_image, (280, 350))

            if self.cur_menu == PLAY_MENU:
                screen.blit(self.cursor_image, (270, 300))
            elif self.cur_menu == QUIT_MENU:
                screen.blit(self.cursor_image, (270, 350))
        elif self.game_state == PLAY:
            screen.blit(self.battlefield.ocean, (0, 0), self.battlefield.offset())
            self.all.draw(screen)
            # self.score_board.draw(screen)

            for i in range(self.plane.power):
                screen.blit(self.plane.power_image, (10 + i * self.plane.power_image.get_width(), 440))
        elif self.game_state == GAMEOVER:
            screen.blit(self.battlefield.ocean, (0, 0), self.battlefield.offset())
            self.enemies.draw(screen)
            # self.score_board.draw(screen)
            screen.blit(self.gameover_image, (272, 150))

    def key_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_UP:
                    self.cursor_sound.play()
                    self.cur_menu -= 1
                    if self.cur_menu < 0:
                        self.cur_menu = 0
                elif event.key == K_DOWN:
                    self.cursor_sound.play()
                    self.cur_menu += 1
                    if self.cur_menu > 1:
                        self.cur_menu = 1
                elif event.key == K_SPACE:
                    if self.game_state == TITLE:
                        self.select_sound.play()
                        if self.cur_menu == PLAY_MENU:
                            self.init_game()
                            self.game_state = PLAY
                        elif self.cur_menu == QUIT_MENU:
                            pygame.quit()
                            sys.exit()
                    elif self.game_state == GAMEOVER:
                        self.game_state = TITLE

    def collide_detection(self):
        for enemy in pygame.sprite.groupcollide(self.enemies, self.shots, 1, 1).keys():
            Explosion(enemy)
            Enemy.bomb_sound.play()
            # self.score_board.add_score(10)

        if not self.plane.invincible:
            if pygame.sprite.spritecollide(self.plane, self.obstacles, 1):
                self.plane.on_invincible()
                # PlaneExplosion(self.plane)
                Plane.bomb_sound.play()
                self.plane.power -= 1
                if self.plane.power == 0:
                    self.game_state = GAMEOVER

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

class SpriteSheet():
    def __init__(self, filename):
        self.sheet = load_image(filename)

    def image_at(self, rect, colorkey=None):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        return image_colorkey(image, colorkey)

    def images_at(self, rects, colorkey=None):
        images = []

        for rect in rects:
            images.append(self.image_at(rect, colorkey))
        return images

class Battlefield():
    speed = 1
    enemy_prob = 12

    def __init__(self):
        w = SCR_RECT.width
        h = SCR_RECT.height
        self.tileside = self.ocean_tile.get_height()
        self.counter = 0
        self.ocean = pygame.Surface((w, h + self.tileside)).convert()

        for y in range(h / self.tileside + 1):
            for x in range(w / self.tileside):
                self.ocean.blit(self.ocean_tile, (x * self.tileside, y * self.tileside))

    def offset(self):
        self.counter = (self.counter - self.speed) % self.tileside
        return (0, self.counter, SCR_RECT.width, SCR_RECT.height)

    def update(self):
        if not random.randrange(self.enemy_prob):
            Enemy()

class Plane(pygame.sprite.Sprite):
    guns = [(17, 19), (39, 19)]
    animcycle = 1
    reload_time = 15

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.on_invincible()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.reload_timer = 0
        self.frame = 0
        self.max_frame = len(self.images) * self.animcycle
        self.power = 3

    def on_invincible(self):
        self.images = self.transparent_images
        self.invincible = True

    def off_invincible(self):
        self.images = self.opaque_images
        self.invincible = False

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.rect = self.rect.clamp(SCR_RECT)
        self.frame = (self.frame + 1) % self.max_frame
        self.image = self.images[self.frame / self.animcycle]

        if self.reload_timer > 0:
            self.reload_timer -= 1

        firing = pygame.mouse.get_pressed()[0]

        if firing and self.reload_timer == 0:
            if self.invincible:
                self.off_invincible()

            self.reload_timer = self.reload_time

            for gun in self.guns:
                Shot((self.rect.left + gun[0], self.rect.top + gun[1]))

class Enemy(pygame.sprite.Sprite):
    gun = (16, 19)
    animcycle = 2
    speed = 3
    shot_prob = 350

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = random.choice(self.image_sets)
        self.image = self.images[0]
        self.frame = 0
        self.max_frame = len(self.images) * self.animcycle
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(SCR_RECT.width - self.rect.width)
        self.rect.bottom = SCR_RECT.top

    def update(self):
        self.rect.move_ip(0, self.speed)
        self.frame = (self.frame + 1) % self.max_frame
        self.image = self.images[self.frame / self.animcycle]

        if self.rect.top > SCR_RECT.bottom:
            self.kill()

        if not random.randrange(self.shot_prob):
            Bomb((self.rect.left + self.gun[0], self.rect.top + self.gun[1]))

class Shot(pygame.sprite.Sprite):
    speed = 9

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        self.rect.move_ip(0, -self.speed)

        if self.rect.top < 0:
            self.kill()

class Bomb(pygame.sprite.Sprite):
    speed = 8

    def __init__(self, gun):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.centery = gun[0], gun[1]
        self.fpx = float(self.rect.centerx)
        self.fpy = float(self.rect.centery)
        angle = math.atan2(self.plane.rect.centery - gun[1], self.plane.rect.centerx - gun[0])
        self.fpdx = self.speed * math.cos(angle)
        self.fpdy = self.speed * math.sin(angle)

    def update(self):
        self.fpx = self.fpx + self.fpdx
        self.fpy = self.fpy + self.fpdy
        self.rect.centerx = int(self.fpx)
        self.rect.centery = int(self.fpy)

        if not SCR_RECT.contains(self.rect):
            self.kill()

class Explosion(pygame.sprite.Sprite):
    animcycle = 4
    def __init__(self, enemy):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.frame = 0
        self.max_frame = len(self.images) * self.animcycle
        self.rect = self.image.get_rect()
        self.rect.center = enemy.rect.center

    def update(self):
        self.image = self.images[self.frame / self.animcycle]
        self.frame += 1

        if self.frame == self.max_frame:
            self.kill()

class PlaneExplosion(pygame.sprite.Sprite):
    pass

class ScoreBoard():
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