import pygame
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.surface.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.day_color = (255,255,255)
        self.current_color = list(self.day_color)
        self.night_color = (38,101,189)
        

    def display(self, time):
        if 6 < time < 17:
            self.full_surf.fill(self.day_color)

        elif 17 < time < 19:
            for index,value in enumerate(self.night_color):
                difference = self.night_color[index] - self.day_color[index]
                scale = (time - 17) /2
                self.current_color[index] = self.day_color[index] + difference * scale
            self.full_surf.fill(self.current_color)
        
        elif 5 < time < 6:
            for index,value in enumerate(self.night_color):
                difference = self.day_color[index] - self.night_color[index]
                scale = (time - 5) 
                self.current_color[index] = difference * scale + self.night_color[index]
            self.full_surf.fill(self.current_color)

        else:
            self.full_surf.fill(self.night_color)

        self.display_surface.blit(self.full_surf, (0,0),special_flags=pygame.BLEND_RGB_MULT)


class Drop(Generic):
    def __init__(self, surf, pos, moving, groups, z):
        # General Setup
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400,500)
        self.start_time = pygame.time.get_ticks()

        # Moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(200,250)

    def update(self, dt):
        # Movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # Timer
        if pygame.time.get_ticks()- self.start_time >= self.lifetime:
            self.kill()

class Rain():
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('graphics/rain/drops/')
        self.rain_floor = import_folder('graphics/rain/floor/')
        self.floor_w, self.floor_h = pygame.image.load('graphics/world/ground.png').get_size()

    def create_floor(self):
        Drop(
            surf = choice(self.rain_floor), 
            pos = (randint(90,self.floor_w),randint(0,self.floor_h)),
            moving = False, 
            groups = [self.all_sprites], 
            z = LAYERS['rain floor'])

    def create_drops(self):
        Drop(
            surf = choice(self.rain_drops), 
            pos = (randint(90,self.floor_w),randint(0,self.floor_h)),
            moving = True, 
            groups = [self.all_sprites], 
            z = LAYERS['rain drops'])

    def update(self):
        self.create_floor()
        self.create_drops()