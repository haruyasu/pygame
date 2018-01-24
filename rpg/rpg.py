# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys, random, os, codecs, struct

SCR_RECT = Rect(0, 0, 640, 480)
GS = 32
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3
STOP, MOVE = 0, 1
PROB_MOVE = 0.005
TRANS_COLOR = (190, 179, 145)
sounds = {}
TITLE, FIELD, TALK, COMMAND, BATTLE_INIT, BATTLE_COMMAND, BATTLE_PROCESS = range(7)

def load_image(dir, file, colorkey=None):
    file = os.path.join(dir, file)
    try:
        image = pygame.image.load(file)
    except pygame.error, message:
        print "Cannot load image:", file
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
            surface = pygame.Surface((GS, GS))
            surface.blit(image, (0, 0), (j, i, GS, GS))
            surface.set_colorkey(surface.get_at((0, 0)), RLEACCEL)
            surface.convert()
            imageList.append(surface)
    return imageList

class PyRPG():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("RPG")

        self.load_sounds("data", "sound.dat")
        self.load_charachips("data", "charachip.dat")
        self.load_mapchips("data", "mapchip.dat")

        self.party = Party()
        player1 = Player("swordman_female", (3, 5), DOWN, True, self.party)
        player2 = Player("elf_female2", (3, 4), DOWN, False, self.party)
        player3 = Player("priestess", (3, 3), DOWN, False, self.party)
        player4 = Player("magician_female", (3, 2), DOWN, False, self.party)
        self.party.add(player1)
        self.party.add(player2)
        self.party.add(player3)
        self.party.add(player4)

        self.map = Map("field", self.party)

        self.msg_engine = MessageEngine()
        self.msgwnd = MessageWindow(Rect(140, 334, 360, 140), self.msg_engine)
        self.cmdwnd = CommandWindow(Rect(16, 16, 216, 160), self.msg_engine)
        self.title = Title(self.msg_engine)
        self.battle = BAttle(self.msgwnd, self.msg_engine)
        global game_state
        game_state = TITLE
        self.mainloop()

    def mainloop(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            self.update()
            self.render()
            pygame.display.update()
            self.check_event()

    def update(self):
        global game_state
        if game_state == TITLE:
            self.title.update()
        elif game_state == FIELD:
            self.map.update()
            self.party.update(self.map)
        elif game_state == TALK:
            self.msgwnd.update()
        elif game_state == BATTLE_INIT or game_state == BATTLE_COMMAND or game_state == BATTLE_PROCESS:
            self.battle.update()
            self.msgwnd.update()

    def render(self):
        global game_state
        if game_state == TITLE:
            self.title.draw(self.screen)
        elif game_state == FIELD or game_state == TALK or game_state == COMMAND:
            offset = self.calc_offset(self.party.member[0])
            self.map.draw(self.screen, offset)
            self.party.draw(self.screen, offset)
            self.msgwnd.draw(self.screen)
            self.cmdwnd.draw(self.screen)
            self.show_info()
        elif game_state in (BATTLE_INIT, BATTLE_COMMAND, BATTLE_PROCESS):
            self.battle.draw(self.screen)
            self.msgwnd.draw(self.screen)

    def check_event(self):
        global game_state
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if game_state == TITLE:
                self.title_handler(event)
            elif game_state == FIELD:
                self.field_handler(event)
            elif game_state == COMMAND:
                self.cmd_handler(event)
            elif game_state == TALK:
                self.talk_handler(event)
            elif game_state == BATTLE_INIT:
                self.battle_init_handler(event)
            elif game_state == BATTLE_COMMAND:
                self.battle_cmd_handler(event)
            elif game_state == BATTLE_PROCESS:
                self.battle_proc_handler(event)

    def title_handler(self, event):
        global game_state
        if event.type == KEYUP and event.key == K_UP:
            self.title.menu -= 1
            if self.title.menu < 0:
                self.title.menu = 0
        elif event.type == KEYDOWN and event.key == K_DOWN:
            self.title.menu += 1
            if self.title.menu > 2:
                self.title.menu = 2
        if event.type == KEYDOWN and event.key == K_SPACE:
            sounds["pi"].play()
            if self.title.menu == Title.START:
                self.game_state = FIELD
                self.map.create("field")
            elif self.title.menu == Title.CONTINUE:
                pass
            elif self.title.menu == Title.EXIT:
                pygame.quit()
                sys.exit()

    def field_handler(self, event):
        global game_state
        if event.type == KEYDOWN and event.key == K_SPACE:
            sounds["pi"].play()
            self.cmdwnd.show()
            game_state = COMMAND

    def cmd_handler(self, event):
        player = self.party.member[0]

        if  event.type == KEYDOWN and event.key == K_LEFT:
            if self.cmdwnd.command <= 3:
                return
            self.cmdwnd.command -= 4
        elif  event.type == KEYDOWN and event.key == K_RIGHT:
            if self.cmdwnd.command >= 4:
                return
            self.cmdwnd.command += 4
        elif  event.type == KEYUP and event.key == K_UP:
            if self.cmdwnd.command == 0 or self.cmdwnd.command == 4:
                return
            self.cmdwnd.command -= 1
        elif  event.type == KEYDOWN and event.key == K_DOWN:
            if self.cmdwnd.command == 3 or self.cmdwnd.command == 7:
                return
            self.cmdwnd.command += 1

        if event.type == KEYDOWN and event.key == K_SPACE:
            if self.cmdwnd.command == CommandWindow.TALK:
                sounds["pi"].play()
                self.cmdwnd.hide()
                chara = player.talk(self.map)
                if chara != None:
                    self.msgwnd.set(chara.message)
                    self.game_state = TALK
                else:
                    self.msgwnd.set("Nobody there!")
                    self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.STATUS:
                sounds["pi"].play()
                self.cmdwnd.hide()
                self.msgwnd.set("STATUS WINDOW")
                self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.EQUIPMENT:
                sounds["pi"].play()
                self.cmdwnd.hide()
                self.msgwnd.set("EQUIPMENT WINDOW")
                self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.DOOR:
                sounds["pi"].play()
                self.cmdwnd.hide()
                door = player.open(self.map)
                if door != None:
                    door.open()
                    self.map.remove_event(door)
                    self.game_state = FIELD
                else:
                    msgwnd.set("No Door")
                    self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.SPELL:
                sounds["pi"].play()
                self.cmdwnd.hide()
                self.msgwnd.set("SPELL WINDOW")
                self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.ITEM:
                sounds["pi"].play()
                self.cmdwnd.hide()
                self.msgwnd.set("ITEM WINDOW")
                self.game_state = TALK
            elif self.cmdwnd.command == CommandWindow.TACTICS:
                sounds["pi"].play()
                self.cmdwnd.hide()
                self.msgwnd.set("TACTICS WINDOW")
                self.game_state = TALK
            elif cmdwnd.command == CommandWindow.SEARCH:
                sounds["pi"].play()
                self.cmdwnd.hide()
                treasure = player.search(self.map)
                if treasure != None:
                    treasure.open()
                    self.msgwnd.set("GET %s" % treasure.item)
                    self.map.remove_event(treasure)
                    self.game_state = TALK
                else:
                    self.msgwnd.set("CAN'T FIND")
                    self.game_state = TALK

    def talk_handler(self, event):
        if event.type == KEYDOWN and event.key == K_SPACE:
            if not self.msgwnd.next():
                self.game_state = FIELD

    def calc_offset(self, player):
        offsetx = player.rect.topleft[0] - SCR_RECT.width / 2
        offsety = player.rect.topleft[1] - SCR_RECT.height / 2
        return offsetx, offsety

    def show_info(self):
        player = self.party.member[0]
        self.msg_engine.draw_string(self.screen, (10, 10), self.map.name.upper())
        self.msg_engine.draw_string(self.screen, (10, 40), player.name.upper())
        self.msg_engine.draw_string(self.screen, (10, 70), "%d_%d" % (player.x, player.y))

    def load_sounds(self, dir, file):
        file = os.path.join(dir, file)
        fp = open(file, "r")
        for line in fp:
            line = line.rstrip()
            data = line.split(",")
            se_name = data[0]
            se_file = os.path.join("se", data[1])
            sounds[se_name] = pygame.mixer.Sound(se_file)
        fp.close()

    def load_charachips(self, dir, file):
        file = os.path.join(dir, file)
        fp = open(file, "r")
        for line in fp:
            line = line.rstrip()
            data = line.split(",")
            chara_id = int(data[0])
            chara_name = data[1]
            Character.images[chara_name] = split_image(load_image("charachip", "%s.png" % chara_name))
        fp.close()

    def load_mapchips(self, dir, file):
        file = os.path.join(dir, file)
        fp = open(file, "r")
        for line in fp:
            line = line.rstrip()
            data = line.split(",")
            mapchip_id = int(data[0])
            mapchip_name = data[1]
            movable = int(data[2])
            transparent = int(data[3])

            if transparent == 0:
                Map.images.append(load_image("mapchip", "%s.png" % mapchip_name))
            else:
                Map.images.append(load_image("mapchip", "%s.png" % mapchip_name, TRANS_COLOR))
            Map.movable_type.append(movable)
        fp.close()

class Map:
    images = []
    movable_type = []
    def __init__(self, name, party):
        self.name = name
        self.row = -1
        self.col = -1
        self.map = []
        self.charas = []
        self.events = []
        self.party = party
        self.load()
        self.load_event()

    def create(self, dest_map):
        self.name = dest_map
        self.charas = []
        self.events = []
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
                if x < 0 or y < 0 or x > self.col - 1 or y > self.row - 1:
                    screen.blit(self.images[self.default], (x * GS - offsetx, y * GS - offsety))
                else:
                    screen.blit(self.images[self.map[y][x]], (x * GS - offsetx, y * GS - offsety))

        for event in self.events:
            event.draw(screen, offset)

        for chara in self.charas:
            chara.draw(screen, offset)

    def is_movable(self, x, y):
        if x < 0 or x > self.col-1 or y < 0 or y > self.row-1:
            return False

        if self.movable_type[self.map[y][x]] == 0:
            return False

        for chara in self.charas:
            if chara.x == x and chara.y == y:
                return False

        for event in self.events:
            if self.movable_type[event.mapchip] == 0:
                if event.x == x and event.y == y:
                    return False
        player = self.party.member[0]
        if player.x == x and player.y == y:
            return False

        return True

    def get_chara(self, x, y):
        for chara in self.charas:
            if chara.x == x and chara.y == y:
                return chara
        return None

    def get_event(self, x, y):
        for event in self.events:
            if event.x == x and event.y == y:
                return event
        return None

    def remove_event(self, event):
        self.events.remove(event)

    def load(self):
        file = os.path.join("data", self.name + ".map")
        fp = open(file, "rb")

        self.row = struct.unpack("i", fp.read(struct.calcsize("i")))[0]
        self.col = struct.unpack("i", fp.read(struct.calcsize("i")))[0]
        self.default = struct.unpack("B", fp.read(struct.calcsize("B")))[0]
        self.map = [[0 for c in range(self.col)] for r in range(self.row)]

        for r in range(self.row):
            for c in range(self.col):
                self.map[r][c] = struct.unpack("B", fp.read(struct.calcsize("B")))[0]
        fp.close()

    def load_event(self):
        file = os.path.join("data", self.name + ".evt")
        fp = codecs.open(file, "r", "utf-8")
        for line in fp:
            line = line.rstrip()
            if line.startswith("#"):
                continue
            data = line.split(",")
            event_type = data[0]
            if event_type == "BGM":
                self.play_bgm(data)
            elif event_type == "CHARA":
                self.create_chara(data)
            elif event_type == "MOVE":
                self.create_move(data)
            elif event_type == "TREASURE":
                self.create_treasure(data)
            elif event_type == "DOOR":
                self.create_door(data)
            elif event_type == "OBJECT":
                self.create_obj(data)

        fp.close()

    def play_bgm(self, data):
        bgm_file = "%s.mp3" % data[1]
        bgm_file = os.path.join("bgm", bgm_file)
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.play(-1)

    def create_chara(self, data):
        name = data[1]
        x, y = int(data[2]), int(data[3])
        direction = int(data[4])
        movetype = int(data[5])
        message = data[6]
        chara = Character(name, (x,y), direction, movetype, message)
        self.charas.append(chara)

    def create_move(self, data):
        x, y = int(data[1]), int(data[2])
        mapchip = int(data[3])
        dest_map = data[4]
        dest_x, dest_y = int(data[5]), int(data[6])
        move = MoveEvent((x, y), mapchip, dest_map, (dest_x, dest_y))
        self.events.append(move)

    def create_treasure(self, data):
        x, y = int(data[1]), int(data[2])
        item = data[3]
        treasure = Treasure((x, y), item)
        self.events.append(treasure)

    def create_door(self, data):
        x, y = int(data[1]), int(data[2])
        door = Door((x, y))
        self.events.append(door)

    def create_obj(self, data):
        x, y = int(data[1]), int(data[2])
        mapchip = int(data[3])
        obj = Object((x, y), mapchip)
        self.events.append(obj)

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

    def set_pos(self, x, y, dir):
        self.x, self.y = x, y
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))
        self.direction = dir

    def __str__(self):
        return "CHARA,%s,%d,%d,%d,%d,%s" % (self.name, self.x, self.y, self.direction, self.movetype, self.message)

class Player(Character):
    def __init__(self, name, pos, dir, leader, party):
        Character.__init__(self, name, pos, dir, False, None)
        self.leader = leader
        self.party = party

    def update(self, map):
        if self.moving == True:
            self.rect.move_ip(self.vx, self.vy)
            if self.rect.left % GS == 0 and self.rect.top % GS == 0:
                self.moving = False
                self.x = self.rect.left / GS
                self.y = self.rect.top / GS

                if not self.leader:
                    return

                event = map.get_event(self.x, self.y)
                if isinstance(event, MoveEvent):
                    sounds["step"].play()
                    dest_map = event.dest_map
                    dest_x = event.dest_x
                    dest_y = event.dest_y
                    map.create(dest_map)

                    for player in self.party.member:
                        player.set_pos(dest_x, dest_y, DOWN)
                        player.moving = False

        self.frame += 1
        self.image = self.images[self.name][self.direction * 4 + self.frame / self.animcycle % 4]

    def move_to(self, destx, desty):
        dx = destx - self.x
        dy = desty - self.y

        if dx == 1:
            self.direction = RIGHT
        elif dx == -1:
            self.direction = LEFT
        elif dy == -1:
            self.direction = UP
        elif dy == 1:
            self.direction = DOWN

        self.vx, self.vy = dx * self.speed, dy * self.speed
        self.moving = True

    def talk(self, map):
        nextx, nexty = self.x, self.y
        if self.direction == DOWN:
            nexty = self.y + 1
            event = map.get_event(nextx, nexty)
            if isinstance(event, Object) and event.mapchip == 41:
                nexty += 1
        elif self.direction == LEFT:
            nextx = self.x - 1
            event = map.get_event(nextx, nexty)
            if isinstance(event, Object) and event.mapchip == 41:
                nextx -= 1
        elif self.direction == RIGHT:
            nextx = self.x + 1
            event = map.get_event(nextx, nexty)
            if isinstance(event, Object) and event.mapchip == 41:
                nextx += 1
        elif self.direction == UP:
            nexty = self.y - 1
            event = map.get_event(nextx, nexty)
            if isinstance(event, Object) and event.mapchip == 41:
                nexty -= 1

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

    def serch(self, map):
        event = map.get_event(self.x, self.y)
        if isinstance(event, Treasure):
            return event
        return None

    def open(self, map):
        nextx, nexty = self.x, self.y
        if self.direction == DOWN:
            nexty = self.y + 1
        elif self.direction == LEFT:
            nextx = self.x - 1
        elif self.direction == RIGHT:
            nextx = self.x + 1
        elif self.direction == UP:
            nexty = self.y - 1

        event = map.get_event(nextx, nexty)
        if isinstance(event, Door):
            return event
        return None

class Party:
    def __init__(self):
        self.member = []

    def add(self, player):
        self.member.append(player)

    def update(self, map):
        for player  in self.member:
            player.update(map)

        if not self.member[0].moving:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_DOWN]:
                self.member[0].direction = DOWN

                if map.is_movable(self.member[0].x, self.member[0].y + 1):
                    for i in range(len(self.member) - 1, 0, -1):
                        self.member[i].move_to(self.member[i - 1].x, self.member[i - 1].y)
                    self.member[0].move_to(self.member[0].x, self.member[0].y + 1)
            elif pressed_keys[K_LEFT]:
                self.member[0].direction = LEFT
                if map.is_movable(self.member[0].x - 1, self.member[0].y):
                    for i in range(len(self.member) - 1, 0, -1):
                        self.member[i].move_to(self.member[i - 1].x, self.member[i - 1].y)
                    self.member[0].move_to(self.member[0].x - 1, self.member[0].y)
            elif pressed_keys[K_RIGHT]:
                self.member[0].direction = RIGHT
                if map.is_movable(self.member[0].x + 1, self.member[0].y):
                    for i in range(len(self.member) - 1, 0, -1):
                        self.member[i].move_to(self.member[i - 1].x, self.member[i - 1].y)
                    self.member[0].move_to(self.member[0].x + 1, self.member[0].y)
            elif pressed_keys[K_UP]:
                self.member[0].direction = UP
                if map.is_movable(self.member[0].x, self.member[0].y - 1):
                    for i in range(len(self.member) - 1, 0, -1):
                        self.member[i].move_to(self.member[i - 1].x, self.member[i - 1].y)
                    self.member[0].move_to(self.member[0].x, self.member[0].y - 1)
    def draw(self, screen, offset):
        for player in self.member[::-1]:
            player.draw(screen, offset)

class MessageEngine:
    FONT_WIDTH = 16
    FONT_HEIGHT = 22
    WHITE, RED, GREEN, BLUE = 0, 160, 320, 480

    def __init__(self):
        self.image = load_image("data", "font.png", -1)
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
        pygame.draw.rect(screen, (0, 0, 0), self.inner_rect, 0)

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
    animcycle = 24

    def __init__(self, rect, msg_engine):
        Window.__init__(self, rect)
        self.text_rect = self.inner_rect.inflate(-32, -32)
        self.text = []
        self.cur_page = 0
        self.cur_pos = 0
        self.next_flag = False
        self.hide_flag = False
        self.msg_engine = msg_engine
        self.cursor = load_image("data", "cursor.png", -1)
        self.frame = 0

    def set(self, message):
        self.cur_pos = 0
        self.cur_page = 0
        self.next_flag = False
        self.hide_flag = False

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
        self.text[p] = "$"
        self.show()

    def update(self):
        if self.is_visible:
            if self.next_flag == False:
                self.cur_pos += 1
                p = self.cur_page * self.MAX_CHARS_PER_PAGE + self.cur_pos

                if self.text[p] == "/":
                    self.cur_pos += self.MAX_CHARS_PER_LINE
                    self.cur_pos = (self.cur_pos / self.MAX_CHARS_PER_LINE) * self.MAX_CHARS_PER_LINE
                elif self.text[p] == "%":
                    self.cur_pos += self.MAX_CHARS_PER_PAGE
                    self.cur_pos = (self.cur_pos / self.MAX_CHARS_PER_PAGE) * self.MAX_CHARS_PER_PAGE
                elif self.text[p] == "$":
                    self.hide_flag = True

                if self.cur_pos % self.MAX_CHARS_PER_PAGE == 0:
                    self.next_flag = True
        self.frame += 1

    def draw(self, screen):
        Window.draw(self, screen)

        if self.is_visible == False:
            return

        for i in range(self.cur_pos):
            ch = self.text[self.cur_page * self.MAX_CHARS_PER_PAGE + i]
            if ch == "/" or ch == "%" or ch == "$":
                continue

            dx = self.text_rect[0] + MessageEngine.FONT_WIDTH * (i % self.MAX_CHARS_PER_LINE)
            dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * (i / self.MAX_CHARS_PER_LINE)
            self.msg_engine.draw_character(screen, (dx, dy), ch)

        if (not self.hide_flag) and self.next_flag:
            if self.frame / self.animcycle % 2 == 0:
                dx = self.text_rect[0] + (self.MAX_CHARS_PER_LINE / 2) * MessageEngine.FONT_WIDTH - MessageEngine.FONT_WIDTH / 2
                dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * 3
                screen.blit(self.cursor, (dx, dy))

    def next(self):
        if self.hide_flag:
            self.hide()
            return False

        if self.next_flag:
            self.cur_page += 1
            self.cur_page = 0
            self.next_flag = False
            return True

class CommandWindow(Window):
    LINE_HEIGHT = 8
    TALK, STATUS, EQUIPMENT, DOOR, SPELL, ITEM, TACTICS, SEARCH = range(0, 8)
    COMMAND = ["TALK", "STATUS", "EQUIPMENT", "DOOR", "SPELL", "ITEM", "TACTICS", "SEARCH"]

    def __init__(self, rect, msg_engine):
        Window.__init__(self, rect)
        self.text_rect = self.inner_rect.inflate(-32, -32)
        self.command = self.TALK
        self.msg_engine = msg_engine
        self.cursor = load_image("data", "cursor2.png", -1)
        self.frame = 0

    def draw(self, screen):
        Window.draw(self, screen)
        if self.is_visible == False:
            return

        for i in range(0, 4):
            dx = self.text_rect[0] + MessageEngine.FONT_WIDTH
            dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * (i % 4)
            self.msg_engine.draw_string(screen, (dx, dy), self.COMMAND[i])

        for i in range(4, 8):
            dx = self.text_rect[0] + MessageEngine.FONT_WIDTH * 6
            dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * (i % 4)
            self.msg_engine.draw_string(screen, (dx, dy), self.COMMAND[i])

        dx = self.text_rect[0] + MessageEngine.FONT_WIDTH * 5 * (self.command /  4)
        dy = self.text_rect[1] + (self.LINE_HEIGHT + MessageEngine.FONT_HEIGHT) * (self.command % 4)
        screen.blit(self.cursor, (dx, dy))

    def show(self):
        self.command = self.TALK
        self.is_visible = True

class MoveEvent():
    def __init__(self, pos, mapchip, dest_map, dest_pos):
        self.x, self.y = pos[0], pos[1]
        self.mapchip = mapchip
        self.dest_map = dest_map
        self.dest_x, self.dest_y = dest_pos[0], dest_pos[1]
        self.image = Map.images[self.mapchip]
        self.rect = self.image.get_rect(topleft=(self.x *GS, self.y * GS))

    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))

    def __str__(self):
        return "MOVE, %d, %d, %d, %s, %d, %d" % (self.x, self.y, self.mapchip, self.dest_map, self.dest_x, self.dest_y)

class Treasure():
    def __init__(self, pos, item):
        self.x, self.y = pos[0], pos[1]
        self.mapchip = 46
        self.image = Map.images[self.mapchip]
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))
        self.item = item

    def open(self):
        sounds["treasure"].play()

    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))

    def __str__(self):
        return "TREASURE, %d, %d, %d" % (self.x, self.y, self.item)

class Door:
    def __init__(self, pos):
        self.x, self.y = pos[0], pos[1]
        self.mapchip = 45
        self.image = Map.images[self.mapchip]
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))

    def open(self):
        sounds["door"].play()

    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))

    def __str__(self):
        return "DOOR, %d, %d" % (self.x, self.y)

class Object:
    def __init__(self, pos, mapchip):
        self.x, self.y = pos[0], pos[1]
        self.mapchip = mapchip
        self.image = Map.images[self.mapchip]
        self.rect = self.image.get_rect(topleft=(self.x * GS, self.y * GS))

    def draw(self, screen, offset):
        offsetx, offsety = offset
        px = self.rect.topleft[0]
        py = self.rect.topleft[1]
        screen.blit(self.image, (px - offsetx, py - offsety))

    def __str__(self):
        return "OBJECT, %d, %d, %d" % (self.x, self.y, mapchip)

class Title:
    START, CONTINUE, EXIT = 0, 1, 2
    def __init__(self, msg_engine):
        self.msg_engine = msg_engine
        self.title_img = load_image("data", "python_quest.png", -1)
        self.cursor_img = load_image("data", "cursor2.png", -1)
        self.menu = self.START
        self.play_bgm()

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 128))
        screen.blit(self.title_img, (20, 60))

        self.msg_engine.draw_string(screen, (260,240), u"ＳＴＡＲＴ")
        self.msg_engine.draw_string(screen, (260,280), u"ＣＯＮＴＩＮＵＥ")
        self.msg_engine.draw_string(screen, (260,320), u"ＥＸＩＴ")

        if self.menu == self.START:
            screen.blit(self.cursor_img, (240, 240))
        elif self.menu == self.CONTINUE:
            screen.blit(self.cursor_img, (240, 280))
        elif self.menu == self.EXIT:
            screen.blit(self.cursor_img, (240, 320))

    def play_bgm(self):
        bgm_file = "title.mp3"
        bgm_file = os.path.join("bgm", bgm_file)
        pygame.mixer.music.load(bgm_file)
        pygame.mixer.music.play(-1)

if __name__ == '__main__':
    PyRPG()
