import pygame
from pygame.locals import *
import sys, random, os

SCR_RECT = Rect(0, 0, 640, 480)
GS = 32
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3
STOP, MOVE = 0, 1
PROB_MOVE = 0.005

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("RPG")

    Character.images["player"] = split_image(load_image("player.png"))
    Character.images["king"] = split_image(load_image("king.png"))
    Character.images["minister"] = split_image(load_image("minister.png"))
    Character.images["soldier"] = split_image(load_image("soldier.png"))

    Map.images[0] = load_image("grass.png")
    Map.images[1] = load_image("water.png")
    Map.images[2] = load_image("forest.png")
    Map.images[3] = load_image("hill.png")
    Map.images[4] = load_image("mountain.png")

    map = Map("test2")
    player = Player("player", (1, 1), DOWN)
    map.add_chara(player)
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        map.update()
        offset = calc_offset(player)
        map.draw(screen, offset)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()

def calc_offset(player):
    offsetx = player.rect.topleft[0] - SCR_RECT.width / 2
    offsety = player.rect.topleft[1] - SCR_RECT.height / 2
    return offsetx, offsety

def load_image(filename, colorkey=None):
    filename = os.path.join("data", filename)

    try:
        image = pygame.image.load(filename)
    except pygame.error, message:
        print "Cannot load image:", filename
        raise SystemExit, message

    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image

def split_image(image):
    imageList = []

    for i in range(0, 128, GS):
        for j in range(0, 128, GS):
            surface = pygame.Surface((GS, GS))
            surface.blit(image, (0, 0), (j, i, GS, GS))
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            surface.convert()
            imageList.append(surface)

    return imageList

class Map:
    images = [None] * 256
    def __init__(self, name):
        self.name = name
        self.row = -1
        self.col = -1
        self.map = []
        self.charas = []
        self.load()

    def add_chara(self, chara):
        self.charas.append(chara)

    def update(self):
        for chara in self.charas:
            chara.update(self)

    def draw(self, screen, offset):
        offsetx, offsety = offset
        startx = offsetx / GS
        endx = startx + SCR_RECT.width / GS + 1
        starty = offsety / GS
        endy = starty + SCR_RECT.height / GS + 1

        for y in range(starty, endy):
            for x in range(startx, endx):
                if x < 0 or y < 0 or x > self.col - 1 or y > self.row - 1:
                    screen.blit(self.images[self.default], (x * GS - offsetx, y * GS - offsety))
                else:
                    screen.blit(self.images[self.map[y][x]], (x * GS - offsetx, y * GS - offsety))

        for chara in self.charas:
            chara.draw(screen, offset)

    def is_movable(self, x, y):
        if x < 0 or x > self.col - 1 or y < 0 or y > self.row - 1:
            return False

        if self.map[y][x] == 1 or self.map[y][x] == 4:
            return False

        for chara in self.charas:
            if chara.x == x and chara.y == y:
                return False

        return True

    def load(self):
        file = os.path.join("data", self.name + ".map")
        fp = open(file)
        lines = fp.readlines()
        row_str, col_str = lines[0].split()
        self.row, self.col = int(row_str), int(col_str)
        self.default = int(lines[1])
        for line in lines[2:]:
            line = line.rstrip()
            self.map.append([int(x) for x in list(line)])
        fp.close()

    def load_event(self):
        file = os.path.join("data", self.name + ".evt")
        fp = codecs.open(file, "r", "utf-8")

        for line in fp:
            line = line.rstrip()
            if line.startwith("#"):
                continue
            data = line.split(',')
            event_type = data[0]
            if event_type == "CAHRA":
                self.create_chara(data)
        fp.close()

    def create_chara(self, data):
        name = data[1]
        x, y = int(data[2]), int(data[3])
        direction = int(data[4])
        movetype = int(data[5])
        message = data[6]
        chara = Character(name, (x, y), direction, movetype, message)
        self.charas.append(chara)

class Character:
    speed = 4
    animcycle = 24
    frame = 0
    images = {}

    def __init__(self, name, pos, dir, movetype, message):
        self.name = name
        self.image = self.images[name][0]
        self.x, self.y = pos[0], pos[1]
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))
        self.vx, self.vy = 0, 0
        self.moving = False
        self.direction = dir
        self.movetype = movetype
        self.message = message

    def update(self, map):
        if self.moving == True:
            self.rect.move_ip(self.vx, self.vy)
            if self.rect.left % GS == 0 and self.rect.top % GS == 0:
                self.moving = False
                self.x = self.rect.left / GS
                self.y = self.rect.top / GS
        elif self.movetype == MOVE and random.random() < PROB_MOVE:
            self.direction = random.randint(0, 3)
            if self.direction == DOWN:
                if map.is_movable(self.x, self.y + 1):
                    self.vx, self.vy = 0, self.speed
                    self.moving = True
            elif self.direction == LEFT:
                if map.is_movable(self.x - 1, self.y):
                    self.vx, self.vy = -self.speed, 0
                    self.moving = True
            elif self.direction == RIGHT:
                if map.is_movable(self.x + 1, self.y):
                    self.vx, self.vy = self.speed, 0
                    self.moving = True
            elif self.direction == UP:
                if map.is_movable(self.x, self.y - 1):
                    self.vx, self.vy = 0, -self.speed
                    self.moving = True

        self.frame += 1
        self.image = self.images[self.name][self.direction * 4 + self.frame / self.animcycle % 4]

    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))

    def __str__(self):
        return "CHARA,%s,%d,%d,%d,%d,%s" % (self.name, self.x, self.y, self.direction, self.movetype, self.message)

class Player(Character):
    def __init__(self, name, pos, dir):
        Character.__init__(self, name, pos, dir, False, None)

    def update(self, map):
        if self.moving == True:
            self.rect.move_ip(self.vx, self.vy)
            if self.rect.left % GS == 0 and self.rect.top % GS == 0:
                self.moving = False
                self.x = self.rect.left / GS
                self.y = self.rect.top / GS
        else:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_DOWN]:
                self.direction = DOWN
                if map.is_movable(self.x, self.y + 1):
                    self.vx, self.vy = 0, self.speed
                    self.moving = True
            elif pressed_keys[K_LEFT]:
                self.direction = LEFT
                if map.is_movable(self.x - 1, self.y):
                    self.vx, self.vy = -self.speed, 0
                    self.moving = True
            elif pressed_keys[K_RIGHT]:
                self.direction = RIGHT
                if map.is_movable(self.x + 1, self.y):
                    self.vx, self.vy = self.speed, 0
                    self.moving = True
            elif pressed_keys[K_UP]:
                self.direction = UP
                if map.is_movable(self.x, self.y - 1):
                    self.vx, self.vy = 0, -self.speed
                    self.moving = True

        self.frame += 1
        self.image = self.images[self.name][self.direction * 4 + self.frame / self.animcycle % 4]

if __name__ == '__main__':
    main()
