#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys, random, os, codecs

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
    Character.images["black_cat"] = split_image(load_image("black_cat.png"))

    Map.images[0] = load_image("grass.png")
    Map.images[1] = load_image("water.png")
    Map.images[2] = load_image("forest.png")
    Map.images[3] = load_image("hill.png")
    Map.images[4] = load_image("mountain.png")

    map = Map("test2")
    player = Player("player", (1, 1), DOWN)
    map.add_chara(player)
    msgwnd = MessageWindow(Rect(140, 334, 360, 140))
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        if not msgwnd.is_visible:
            map.update()
        offset = calc_offset(player)
        map.draw(screen, offset)
        msgwnd.draw(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_SPACE:
                if msgwnd.is_visible:
                    msgwnd.next()
                else:
                    chara = player.talk(map)
                    if chara != None:
                        msgwnd.set(chara.message)
                    else:
                        msgwnd.set("Nobody anymore!")

def calc_offset(player):
    offsetx = player.rect.topleft[0] - SCR_RECT.width/2
    offsety = player.rect.topleft[1] - SCR_RECT.height/2
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
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def split_image(image):
    imageList = []
    for i in range(0, 128, GS):
        for j in range(0, 128, GS):
            surface = pygame.Surface((GS,GS))
            surface.blit(image, (0,0), (j,i,GS,GS))
            surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
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
        self.load_event()

    def add_chara(self, chara):
        self.charas.append(chara)

    def update(self):
        for chara in self.charas:
            chara.update(self)

    def draw(self, screen, offset):
        offsetx, offsety = offset
        startx = offsetx / GS
        endx = startx + SCR_RECT.width/GS + 1
        starty = offsety / GS
        endy = starty + SCR_RECT.height/GS + 1
        for y in range(starty, endy):
            for x in range(startx, endx):
                if x < 0 or y < 0 or x > self.col-1 or y > self.row-1:
                    screen.blit(self.images[self.default], (x*GS-offsetx,y*GS-offsety))
                else:
                    screen.blit(self.images[self.map[y][x]], (x*GS-offsetx,y*GS-offsety))
        for chara in self.charas:
            chara.draw(screen, offset)

    def is_movable(self, x, y):
        if x < 0 or x > self.col-1 or y < 0 or y > self.row-1:
            return False
        if self.map[y][x] == 1 or self.map[y][x] == 4:
            return False
        for chara in self.charas:
            if chara.x == x and chara.y == y:
                return False
        return True

    def get_chara(self, x, y):
        for chara in self.charas:
            if chara.x == x and chara.y == y:
                return chara
        return None

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
            if line.startswith("#"): continue
            data = line.split(",")
            event_type = data[0]
            if event_type == "CHARA":
                self.create_chara(data)
        fp.close()

    def create_chara(self, data):
        name = data[1]
        x, y = int(data[2]), int(data[3])
        direction = int(data[4])
        movetype = int(data[5])
        message = data[6]
        chara = Character(name, (x,y), direction, movetype, message)
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

    def talk(self, map):
        nextx, nexty = self.x, self.y
        if self.direction == DOWN:
            nexty = self.y + 1
        elif self.direction == LEFT:
            nextx = self.x - 1
        elif self.direction == RIGHT:
            nextx = self.x + 1
        elif self.direction == UP:
            nexty = self.y - 1

        chara = map.get_chara(nextx, nexty)

        if chara != None:
            if self.direction == DOWN:
                chara.direction = UP
            elif self.direction == LEFT:
                chara.direction = RIGHT
            elif self.direction == RIGHT:
                chara.direction = LEFT
            elif self.direction == UP:
                chara.direction = DOWN

            chara.update(map)
        return chara

class MessageEngine:
    FONT_WIDTH = 16
    FONT_HEIGHT = 22
    WHITE, RED, GREEN, BLUE = 0, 160, 320, 480

    def __init__(self):
        self.image = load_image("font.png", -1)
        self.color = self.WHITE
        self.kana2rect = {}
        self.create_hash()

    def set_color(self, color):
        self.color = color
        if not self.color in [self.WHITE,self.RED,self.GREEN,self.BLUE]:
            self.color = self.WHITE

    def draw_character(self, screen, pos, ch):
        x, y = pos
        try:
            rect = self.kana2rect[ch]
            screen.blit(self.image, (x,y), (rect.x+self.color,rect.y,rect.width,rect.height))
        except KeyError:
            print "You can't display! :%s" % ch
            return

    def draw_string(self, screen, pos, str):
        x, y = pos
        for i, ch in enumerate(str):
            dx = x + self.FONT_WIDTH * i
            self.draw_character(screen, (dx,y), ch)

    def create_hash(self):
        filepath = os.path.join("data", "kana2rect.dat")
        fp = codecs.open(filepath, "r", "utf-8")
        for line in fp.readlines():
            line = line.rstrip()
            d = line.split(" ")
            kana, x, y, w, h = d[0], int(d[1]), int(d[2]), int(d[3]), int(d[4])
            self.kana2rect[kana] = Rect(x, y, w, h)
        fp.close()

class Window:
    EDGE_WIDTH = 4
    def __init__(self, rect):
        self.rect = rect
        self.inner_rect = self.rect.inflate(-self.EDGE_WIDTH * 2, -self.EDGE_WIDTH * 2)
        self.is_visible = False

    def draw(self, screen):
        if self.is_visible == False:
            return
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 0)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 0)

    def show(self):
        self.is_visible = True

    def hide(self):
        self.is_visible = False


class MessageWindow(Window):
    MAX_CHARS_PER_LINE = 20
    MAX_LINES_PER_PAGE = 3
    MAX_CHARS_PER_PAGE = 20 * 3
    MAX_LINES = 30
    LINE_HEIGHT = 8

    def __init__(self, rect):
        Window.__init__(self, rect)
        self.text_rect = self.inner_rect.inflate(-32, -32)
        self.text = []
        self.cur_page = 0
        self.max_page = 0
        self.msg_engine = MessageEngine()
        self.cursor = load_image("cursor.png", -1)

    def set(self, message):
        self.cur_page = 0
        self.text = [u'　'] * (self.MAX_LINES * self.MAX_CHARS_PER_LINE)
        p = 0
        for i in range(len(message)):
            ch = message[i]
            if ch == "/":
                self.text[p] = "/"
                p += self.MAX_CHARS_PER_LINE
                p = (p / self.MAX_CHARS_PER_LINE) * self.MAX_CHARS_PER_LINE
            elif ch == "%":
                self.text[p] = "%"
                p += self.MAX_CHARS_PER_PAGE
                p = (p / self.MAX_CHARS_PER_PAGE) * self.MAX_CHARS_PER_PAGE
            else:
                self.text[p] = ch
                p += 1
        self.max_page = p / self.MAX_CHARS_PER_PAGE
        self.show()

    def draw(self, screen):
        Window.draw(self, screen)
        if self.is_visible == False: return
        for i in range(self.MAX_CHARS_PER_PAGE):
            ch = self.text[self.cur_page * self.MAX_CHARS_PER_PAGE + i]
            if ch == "/" or ch == "%": continue
            dx = self.text_rect[0] + MessageEngine.FONT_WIDTH * (i % self.MAX_CHARS_PER_LINE)
            dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * (i / self.MAX_CHARS_PER_LINE)
            self.msg_engine.draw_character(screen, (dx, dy), ch)
        if self.cur_page < self.max_page:
            dx = self.text_rect[0] + (self.MAX_CHARS_PER_LINE / 2) * MessageEngine.FONT_WIDTH - MessageEngine.FONT_WIDTH / 2
            dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * 3
            screen.blit(self.cursor, (dx, dy))

    def next(self):
        if self.cur_page == self.max_page:
            self.hide()
        self.cur_page += 1

if __name__ == '__main__':
    main()
