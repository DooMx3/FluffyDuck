from random import randint, choice

import pygame
import pygame.event


class StartScreen:
    INST01 = "Press space to start"
    INST15 = "Press R to get ready"
    INST02 = "Press M for multiplayer"
    SUBTITLE = "MULTIPLAYER"

    def __init__(self):
        title_font = pygame.font.Font("res/Turret_Road/TurretRoad-ExtraBold.ttf", 144)
        subtitle_font = pygame.font.Font("res/Turret_Road/TurretRoad-Bold.ttf", 64)
        inst_font = pygame.font.Font("res/Turret_Road/TurretRoad-ExtraLight.ttf", 32)
        self.title_text = title_font.render("Fluffy Duck", True, (0, 0, 0))
        self.subtitle = subtitle_font.render(self.SUBTITLE, True, (240, 0, 0))
        self.inst1 = inst_font.render(self.INST01, True, (0, 0, 0))
        self.inst15 = inst_font.render(self.INST15, True, (0, 0, 0))
        self.inst2 = inst_font.render(self.INST02, True, (0, 0, 0))

    def draw(self, window, is_multiplayer):
        window.blit(self.title_text, (10, 10))
        h = self.title_text.get_height()
        if is_multiplayer:
            window.blit(self.subtitle, (40, h + 10))
            h += self.subtitle.get_height() + 20

        if is_multiplayer:
            window.blit(self.inst15, (20, h + 30))
        else:
            window.blit(self.inst1, (20, h + 30))

        if not is_multiplayer:
            h += self.inst1.get_height() + 30
            window.blit(self.inst2, (20, h))


class Background:
    def __init__(self):
        self.block_img = pygame.image.load("res/buildings.png")
        self.grass_img = pygame.image.load("res/grass.png")

    def draw(self, window: pygame.Surface):
        window.blit(self.block_img, (0, 470))
        window.blit(self.grass_img, (0, 530))


class Foreground:
    FORWARD = 2
    SPEEDUP_RATE = 1.4

    def __init__(self, poles_amount):
        self.poles = []
        self.potions = []
        self.forward_speed = self.FORWARD
        self.player_x = Player.X
        self.player_vel = 0
        x = 300
        for _ in range(poles_amount):
            y = randint(185, 585)
            self.poles.append(Pole(x, y, randint(190, 240)))
            addx = randint(250, 300)
            x += addx
            if randint(1, 6) == 2:
                potion_y = randint(10, 560)
                self.potions.append(Potion(choice((Potion.BOOST, Potion.PEN)), x - (addx // 2 - 30), potion_y))
        self.fline = FinishingLine(x + 400)
        self.turn_clock = 0
        self.speedup_clock = 0
        self.boost_clock = 0
        self.speedup_rate = self.SPEEDUP_RATE
        self.other_direction = False
        self.speedup = False
        self.boost = False
        self.one_pen = False

    def f_line_tick(self, *args, **kwargs):
        return self.fline.tick(*args, **kwargs)

    def tick(self, player, events, delta_time):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.forward_speed = self.FORWARD * self.speedup_rate
                    self.speedup = True
        if self.other_direction:
            self.move_poles(-1)
        else:
            self.move_poles(self.forward_speed)
        for pole in self.poles:
            if pole.collide(player.hitbox):
                if self.one_pen:
                    pole.deactivate()
                    self.one_pen = False
                else:
                    self.other_direction = True

        for potion in self.potions:
            if potion.tick(player):
                self.do_effect(potion.type_)

        if self.other_direction:
            self.turn_clock += delta_time

        if self.speedup:
            self.speedup_clock += delta_time

        if self.boost:
            self.boost_clock += delta_time

        if self.turn_clock > randint(8, 23) / 10:
            self.other_direction = False
            self.turn_clock = 0

        if self.speedup_clock > 0.5:
            self.speedup_clock = 0
            self.forward_speed = self.FORWARD
            self.speedup = False

        if self.boost_clock > 5:
            self.boost = False
            self.speedup_rate = self.SPEEDUP_RATE
            self.boost_clock = 0

    def move_poles(self, x):
        self.player_vel = x
        self.fline.x -= x
        self.player_x += x
        for pole in self.poles:
            pole.move(x)

        for potion in self.potions:
            potion.move(x)

    def draw(self, window):
        for pole in self.poles:
            pole.draw(window)

        for potion in self.potions:
            potion.draw(window)

        self.fline.draw(window)

    def do_effect(self, type_):
        if type_ == Potion.BOOST:
            self.boost = True
            self.speedup_rate = self.SPEEDUP_RATE * 2
        if type_ == Potion.PEN:
            self.one_pen = True


class Pole:
    def __init__(self, x, y, gape=175):
        self.image_down = pygame.image.load("res/pole.png")
        self.image_up = pygame.transform.flip(self.image_down, False, True)
        self.x = x
        self.y = y
        self.gape = gape
        self.hitbox = pygame.Rect(self.x, self.y, 60, 600)
        self.hitbox2 = pygame.Rect(self.x, self.y - 600 - self.gape, 60, 600)
        self.active = True

    def move(self, x):
        self.x -= x
        self.hitbox = pygame.Rect(self.x, self.y, 60, 600)
        self.hitbox2 = pygame.Rect(self.x, self.y - 600 - self.gape, 60, 600)

    def collide(self, hitbox: pygame.Rect):
        return (hitbox.colliderect(self.hitbox) or hitbox.colliderect(self.hitbox2)) and self.active

    def deactivate(self):
        self.active = False
        self.image_down.set_alpha(128)
        self.image_up.set_alpha(128)

    def draw(self, window):
        window.blit(self.image_up, (self.x, self.y - 600 - self.gape))
        window.blit(self.image_down, (self.x, self.y))
        # pygame.draw.rect(window, (0, 255, 0), self.hitbox)
        # pygame.draw.rect(window, (0, 255, 0), self.hitbox2)


class FinishingLine:
    def __init__(self, x):
        self.image = pygame.image.load("res/meta.png")
        self.x = x
        self.hitbox = pygame.Rect(x + 50, 0, 50, 600)
        self.finished = False

    def tick(self, player):
        self.hitbox = pygame.Rect(self.x + 50, 0, 50, 600)
        if player.hitbox.colliderect(self.hitbox):
            self.finished = True
            return True

    def draw(self, window):
        window.blit(self.image, (self.x, 0))


class Potion:
    BOOST = 10
    PEN = 11

    def __init__(self, type_, x, y):
        self.type_ = type_
        self.x = x
        self.y = y
        self.hitbox = pygame.Rect(x, y, 30, 30)
        self.active = True

        if type_ == self.BOOST:
            self.image = pygame.image.load("res/bowl_boost.png")
        elif type_ == self.PEN:
            self.image = pygame.image.load("res/bowl_pen.png")
        else:
            self.image = pygame.Surface((30, 30))

    def move(self, x, y=None):
        self.x -= x
        self.y -= y if y is not None else 0
        self.hitbox = pygame.Rect(self.x, self.y, 30, 30)

    def tick(self, player):
        if not self.active:
            return

        if player.hitbox.colliderect(self.hitbox):
            self.active = False
            return True
        return False

    def draw(self, window):
        if self.active:
            window.blit(self.image, (self.x, self.y))


class Bird:
    ANIM_FPS = 7

    def __init__(self, x, y, main_bird):
        if main_bird:
            folder = "bird"
        else:
            folder = "other bird"
        self.images = [pygame.image.load(f"res/{folder}/bird0{frame}.png")
                       for frame in range(1, 6)]
        self.cur_frame = 4
        self.frame_time = 0
        self.x = x
        self.y = y

    def btick(self, delta_time):
        self.frame_time += delta_time
        if self.frame_time > 1 / self.ANIM_FPS:
            self.frame_time = 0
            if self.cur_frame < 4:
                self.cur_frame += 1
            else:
                self.cur_frame = 0

    def draw(self, window):
        window.blit(self.images[self.cur_frame], (self.x, self.y))


class Player(Bird):
    X = 100
    BOOST = 17
    MAX_VEL = 14
    GRAVITY = 0.3

    def __init__(self, main_bird=False, uuid: str = None):
        super().__init__(self.X, 300, main_bird)
        self.main_bird = main_bird
        self.uuid = uuid
        self.ver_velocity = 0
        self.rotated_image = self.cur_frame
        self.hitbox = pygame.Rect(self.x + 20, self.y, 50, 50)

    def refresh_hitbox(self):
        self.hitbox = pygame.Rect(self.x + 20, self.y, 50, 50)

    def refresh_pos(self, x, y, ver_vel):
        self.x = x
        self.y = y
        self.ver_velocity = ver_vel

    def tick(self, delta_time, events: list[pygame.event.Event]):
        super().btick(delta_time)
        if self.y > 545 and self.ver_velocity > -self.GRAVITY:
            self.ver_velocity = 0
        elif abs(self.ver_velocity + self.GRAVITY) <= self.MAX_VEL:
            self.ver_velocity += self.GRAVITY

        if self.main_bird:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.ver_velocity = -8

        self.y += self.ver_velocity
        if self.y < -10:
            self.ver_velocity = 1
        self.refresh_hitbox()

    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.images[self.cur_frame], self.ver_velocity * -2)
        window.blit(rotated_image, (self.x, self.y))
        # pygame.draw.rect(window, (255, 0, 0), self.hitbox)
