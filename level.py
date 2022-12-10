import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from support import import_folder
from pytmx.util_pygame import load_pygame
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu

class Level():
    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites,self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # Sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # Shop
        self.menu = Menu(self.player,self.toggle_shop)
        self.shop_active = False

        # Music
        self.success = pygame.mixer.Sound('audio/success.wav')
        self.success.set_volume(0.3)
        self.music = pygame.mixer.Sound('audio/music.mp3')
        self.music.set_volume(0.1)
        self.music.play(loops = -1)

    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        # House
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surface,self.all_sprites,LAYERS['house bottom'])

        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y,surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surface,self.all_sprites,LAYERS['main'])

        # Fence
        for x,y,surface in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),surface,[self.all_sprites,self.collision_sprites])

        # Water
        water_frames = import_folder('graphics/water')
        for x,y,surface in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE),water_frames,self.all_sprites)

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups = [self.all_sprites,self.collision_sprites, self.tree_sprites],
                name = obj.name,
                player_add = self.player_add
                )

        # Flowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])

        # Collision tiles
        for x,y,surface in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites)

        # Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos = (obj.x,obj.y),
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop = self.toggle_shop)

            elif obj.name == 'Bed':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

            elif obj.name == 'Trader':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)


        Generic((0,0),pygame.image.load('graphics/world/ground.png').convert_alpha(),self.all_sprites,LAYERS['ground']) 

    def player_add(self,item, amount):
        self.player.item_inventory[item] += amount
        self.success.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        # Plants
        self.soil_layer.update_plants()

        # Apples on trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # Rain
        self.raining = randint(0,10) > 7

        # Soil
        self.soil_layer.remove_water()
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # sky
        self.sky.current_color = self.sky.start_color.copy()

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type,1)
                    plant.kill()
                    Particle(pos = plant.rect.topleft, surf = plant.image, groups = (self.all_sprites), z = LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery//TILE_SIZE][plant.rect.centerx//TILE_SIZE].remove('P')

    def run(self,dt):

        # Drawing Logic
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # Updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
        
        # Weather
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        # Transition overlay
        if self.player.sleep:
            self.transition.play(dt)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
                if sprite.z  == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image,offset_rect)
                    
