from pygame.math import Vector2

# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# overlay positions
OVERLAY_POSITIONS = {
    'tool': (40,SCREEN_HEIGHT - 15),
    'seed': (70,SCREEN_HEIGHT-5)
}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-50,40),
    'right': Vector2(50,40),
    'up':Vector2(0,-10),
    'down': Vector2(0,50)
}

LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops':10,
    'overlay': 11
}

APPLE_POS = {
    'Small': [(18,17), (30,37),(12,50),(30,45),(20,30),(30,10)],
    'Large': [(30,24), (60,65), (50,50),(16,40),(45,50),(42,70)]
}

PLANT_TYPES = ['corn','tomato']

plants = open('plants.txt','r')

GROW_SPEED = {

}

SALE_PRICES = {
    'wood': 4,
    'apple': 2,

}

PURCHASE_PRICES = {

}

for plant in PLANT_TYPES:
    line = plants.readline().split(',')
    print(line)
    GROW_SPEED[plant] = float(line[1])
    SALE_PRICES[plant] = int(line[2])
    PURCHASE_PRICES[plant] = int(line[3])


print(PURCHASE_PRICES)



