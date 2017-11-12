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
        self.game_state = START
        self.all = pygame.sprite.RenderUpdates()
        self.aliens = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()
        self.beams = pygame.sprite.Group()

        Player.containers = self.all
        Shot.containers = self.all, self.shots
        Alien.containers = self.all, self.aliens
        Beam.containers = self.all, self.beams
        Explosion.containers = self.all

        self.player = Player()

        for i in range(0, 50):
            x = 20 + (i % 10) * 40
            y = 20 + (i / 10) * 40
            # Alien((x, y))

    def update(self):
        if self.game_state == PLAY:
            self.all.update()
            self.collision_detection()
            if len(self.aliens.sprites()) == 0:
                self.game_state = GAMEOVER

    def draw(self, screen):
        screen.fill((0, 0, 0))
        if self.game_state == START:
            title_font = pygame.font.SysFont(None, 80)
            title = title_font.render("INVADER GAME", False, (204, 51, 0))
            screen.blit(title, ((SCR_RECT.width - title.get_width()) / 2, 100))

            alien_image = Alien.images[0]
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2 + 30, 200))
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2, 200))
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2 - 30, 200))

            player_imagee = Player.image
            screen.blit(player_imagee, ((SCR_RECT.width - player_imagee.get_width()) / 2, 240))

            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255, 255, 255))
            screen.blit(push_space, ((SCR_RECT.width - push_space.get_width()) / 2, 300))

            credit_font = pygame.font.SysFont(None, 20)
            credit = credit_font.render("Haruyasu Kaitori", False, (255, 255, 255))
            screen.blit(credit, ((SCR_RECT.width - credit.get_width())/ 2, 380))
        elif self.game_state == PLAY:
            self.all.draw(screen)
        elif self.game_state == GAMEOVER:
            gameover_font = pygame.font.SysFont(None, 80)
            gameover = gameover_font.render("GAME OVER", False, (255, 0, 0))
            screen.blit(gameover, ((SCR_RECT.width - gameover.get_width())/ 2, 100))

            alien_image = Alien.images[0]
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2 + 30, 200))
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2, 200))
            screen.blit(alien_image, ((SCR_RECT.width - alien_image.get_width()) / 2 - 30, 200))

            player_imagee = Player.image
            screen.blit(player_imagee, ((SCR_RECT.width - player_imagee.get_width()) / 2, 240))

            push_font = pygame.font.SysFont(None, 40)
            push_space = push_font.render("PUSH SPACE KEY", False, (255, 255, 255))
            screen.blit(push_space, ((SCR_RECT.width - push_space.get_width()) / 2, 300))

            credit_font = pygame.font.SysFont(None, 20)
            credit = credit_font.render("Haruyasu Kaitori", False, (255, 255, 255))
            screen.blit(credit, ((SCR_RECT.width - credit.get_width())/ 2, 380))

    def key_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.game_state == START:
                    self.game_state = PLAY
                elif self.game_state == GAMEOVER:
                    self.init_game()
                    self.game_state = PLAY

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