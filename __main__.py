from enum import Enum
from helpbrowser import open_help_document
from opensimplex import OpenSimplex
import pygame
import random
import json
import os
import time
import uuid


# Globals
global menu_open
global item_icon

# Init pygame
pygame.init()

# Variables
fonts = {}
tilesets = {}
default_font = None
default_tileset = None
world = []
worldTiles = []
cameraFollowsPlayer = True
oldmap = []
worldSurface = None
worldEntities = []
menus = []
menu_open = None
item_icon = None

# TODO: Add keymap for config
keymap = {}

# SpriteSheet class
class SpriteSheet(object):
    ''' Class used to grab images out of a sprite sheet. '''

    def __init__(self, file_name, tile_width, tile_height):
        ''' Constructor. Pass in the file name of the sprite sheet. '''

        # Set tile size
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, x, y):
        ''' Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. '''

        # Create a new blank image
        image = pygame.Surface([self.tile_width, self.tile_height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x*self.tile_width, y*self.tile_height, self.tile_width, self.tile_height))

        # Assuming black works as the transparent color
        image.set_colorkey((0, 0, 0))

        # Return the image
        return image

# Camera class
class Camera:
    def __init__(self, x=0, y=0, sx=1, sy=1):
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy

# Console class
class Console:
    def print_message(self, a, b):
        print('[{0}] {1}'.format(a, b))

    def info(self, s):
        self.print_message('INFO', s)

    def warn(self, s):
        self.print_message('WARN', s)

    def error(self, s):
        self.print_message('ERROR', s)

    def severe(self, s):
        self.print_message('SEVERE', s)


# Entity class
class Entity:
    def __init__(self, name, image, x, y, z, health, tangible):
        self.name = name
        self.image = image
        self.x = x
        self.y = y
        self.z = z
        self.health = health
        self.tangible = tangible

    def take_damage(self, damage):
        self.health -= damage

# Text class
class Text:
    x = 0
    y = 0

    def __init__(self, text, font='default', x=0, y=0, fg=(255,255,255), bg=None):
        self.font = fonts[font]
        self.text = text
        self.fg = fg
        self.bg = bg
        self.x = x
        self.y = y
        self.text_object = self.font.render(self.text, 0, self.fg, self.bg)

    def set_text(self, t):
        self.text = t
        self.update()

    def update(self):
        self.text_object = self.font.render(self.text, 0, self.fg, self.bg)

    def draw(self, surface, x=x, y=y):
        surface.blit(self.text_object, (x, y))

# Stats class
class StatsObject:
    def __init__(self, health, strength, agility, dexterity, intelligence):
        self.health = health
        self.strength = strength
        self.agility = agility
        self.dexterity = dexterity
        self.intelligence = intelligence

# Item Stats class
class ItemStats:
    def __init__(self, attack=0, defense=0, health=0, strength=0, agility=0, dexterity=0, intelligence=0):
        self.health = health
        self.attack = attack
        self.defense = defense
        self.strength = strength
        self.agility = agility
        self.dexterity = dexterity
        self.intelligence = intelligence

# Status Effect class
class StatusEffect:
    def __init__(self, name, turns):
        self.name = name
        self.turns = turns

# Item Status Effect class
class ItemStatusEffect:
    def __init__(self, effect, chance):
        self.effect = effect
        self.chance = chance

# Item class
class Item:
    id = 'undefined'
    name = 'undefined'
    stats = ItemStats(0, 0, 0, 0, 0, 0, 0)
    effects = []
    wearable = False
    price = 0
    icon = None

    def on_attack(self, target):
        target.take_damage(self.stats.attack)

    def on_drop(self):
        return

    def on_wear(self):
        return

    def on_break(self):
        return

# Player class
class Player:
    def __init__(self, x, y, z, image, exp, stats, inventory, selected_item):
        self.x = x
        self.y = y
        self.z = z
        self.image = image
        self.exp = exp
        self.stats = stats
        self.inventory = inventory
        self.selected_item = selected_item

    def draw(self):
        screen.blit(self.image, (config['screen']['height'] / 2, config['screen']['width'] / 2))

# Animal Entity class
class AnimalEntity(Entity):
    def do_turn(self):
        try:
            m = random.randint(-1, 1)
            dx = 0
            dy = 0

            if random.randint(0, 1):
                dx = m
            else:
                dy = m

            if world_height > self.y + dy > 0 and world_width > self.x + dx > 0 and player.x != dx + self.x and player.y != dy + self.y:
                if not worldTiles[self.z][self.y + dy][self.x + dx].tangible:
                    self.y += dy
                    self.x += dx
        except Exception as ex:
            console.warn('AnimalAI had a error: ' + str(ex))

# Fast Animal Entity class
class FastAnimalEntity(Entity):
    def do_turn(self):
        try:
            dy = random.randint(-1, 1)
            dx = random.randint(-1, 1)

            if world_height > self.y + dy > 0 and config['world'][
                'width'] > self.x + dx > 0 and player.x != dx + self.x and player.y != dy + self.y:
                if not worldTiles[self.z][self.y + dy][self.x + dx].tangible:
                    self.y += dy
                    self.x += dx
        except Exception as ex:
            console.warn('AnimalAI had a error: ' + str(ex))

# Tile class
class Tile:
    def __init__(self, name, x, y, z, tangible, image):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.tangible = tangible
        self.image = image

# Entity Info Indicator class
class EntityInfoIndicator:
    def __init__(self, entity):
        self.entity = entity
        self.surface = pygame.Surface((128, 48))

    def draw(self):
        # Set X and Y of title
        titleX = config['indicators']['image']['padding_left'] + 32 + config['indicators']['title']['padding_left']
        titleY = config['indicators']['title']['padding_top']

        # Set X and Y of title
        hpX = config['indicators']['image']['padding_left'] + 32 + config['indicators']['hp']['padding_left']
        hpY = config['indicators']['hp']['padding_top'] + config['indicators']['title']['padding_top'] + default_font.size(self.entity.name)[1]

        # Fill screen with color
        self.surface.fill(config['indicators']['background'])

        # Draw to surface
        self.surface.blit(self.entity.image, (config['indicators']['image']['padding_left'], config['indicators']['image']['padding_top']))
        Text(text=self.entity.name).draw(self.surface, x=titleX, y=titleY)
        Text(text='HP: {0}'.format(self.entity.health)).draw(self.surface, x=hpX, y=hpY)

        # Draw to screen
        screen.blit(self.surface, (config['screen']['height'] - 128, 0))

# Select inventory item function
def select_inventory_item(args):
    item = args['item']
    console.info('Selected inventory item {0}'.format(item))
    player.selected_item = item

# Menu Item class
class MenuItem:
    def __init__(self, text, action, args={}, disabled=False):
        self.text = text
        self.action = action
        self.args = args
        self.disabled = disabled

# Menu class
class Menu:
    def __init__(self, name, title, toggle_key, items, x, y):
        self.name = name
        self.title = title
        self.toggle_key = toggle_key
        self.x = x
        self.y = y
        self.items = items
        self.isOpen = False
        self.selectedItem = 0

        s = [self.title]
        for i in self.items:
            s.append(i.text)

        self.surface = pygame.Surface(
            (
                default_font.size(max(s, key=len))[0] + config['menu']['margin_left'] + config['menu'][
                    'margin_right'],
                default_font.size(max(s, key=len))[1] * (len(items) + 1)
            )
        )

    def open(self):
        global menu_open
        self.isOpen = True
        menu_open = self

    def close(self):
        global menu_open
        self.isOpen = False
        menu_open = None

    def toggle(self):
        global menu_open
        self.isOpen = not self.isOpen

        if self.isOpen:
            menu_open = self
        else:
            menu_open = None

    def draw(self, target_surface):
        if self.isOpen:
            self.surface.fill(config['menu']['colors']['background'])

            tt = Text(text=self.title, fg=config['menu']['colors']['title'])
            tt.draw(surface=self.surface,
                    x=int((self.surface.get_width() - tt.text_object.get_size()[0]) / 2),
                    y=config['menu']['margin_top'])
            for i in self.items:
                Text(text=(i.text),
                     fg=config['menu']['colors']['selected']
                     if self.selectedItem == self.items.index(i)
                     else config['menu']['colors']['default']).draw(
                        surface=self.surface,
                        y=default_font.get_height() * (self.items.index(i) + 1) + config['menu']['margin_top'],
                        x=config['menu']['margin_left'])
            target_surface.blit(self.surface, (self.x, self.y))

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selectedItem -= 1
            if self.selectedItem < 0:
                self.selectedItem = len(self.items) - 1
        elif key == pygame.K_DOWN:
            self.selectedItem += 1
            if self.selectedItem > len(self.items) - 1:
                self.selectedItem = 0
        elif key == pygame.K_RETURN:
            self.items[self.selectedItem].action(self.items[self.selectedItem].args)
            self.close()

'''Begin Items'''

class ItemSword(Item):
    id = 'sword'
    name = 'Sword'
    stats = ItemStats(attack=5)
    price = 5

class ItemHammer(Item):
    id = 'hammer'
    name = 'Hammer'
    stats = ItemStats(attack=3, dexterity=2)
    price = 5

'''End items'''

# Stairwell Tile Structure
class StairwellTileStructure(Tile):
    stairwell_direction = None

    def setup(self):
        if self.z != world_depth - 1:
            self.stairwell_direction = random.randint(0, 1)
            d = 1 if self.stairwell_direction == 1 else -1
            osw = StairwellTileStructure(z=self.z + d, y=self.y, x=self.x, name='stairwell', tangible=self.tangible, image=self.image)
            osw.stairwell_direction = not self.stairwell_direction
            worldTiles[self.z + d][self.y][self.x] = osw
            print (worldTiles[self.z - 1][self.y][self.x])
# Add items to classes
items = [
    Item,
    ItemSword,
    ItemHammer
]

# Entity classes
entity_classes = {
    'animal': AnimalEntity,
    'fast_animal': FastAnimalEntity
}

# Tile structure classes
tile_structure_classes = {
    'stairwell': StairwellTileStructure
}

# Read json file function
def read_json_file(fn):
    f = open(fn, 'r')
    d = json.load(f)
    f.close()
    return d

# Quit game function
def quit_game(args={}):
    console.info('Quitting game')
    exit()

def restart_game(args={}):
    console.info('Restarting game')

# Entity collision function
def check_entity_collision(x, y, z):
    for i in worldEntities:
        if i.y == y and i.x == x and i.z == z and i.tangible:
            return True
    return False

# Get inventory items function
def get_inventory_menuitems():
    o = []
    for i in player.inventory:
        o.append(MenuItem(text=i.name, action=select_inventory_item, args={'item': i}))
    return o

# Open help document function
def open_help(args):
    open_help_document(page=args['page'], title=args['title'] if args['title'] else 'Hep[ Browser')

# Create console
console = Console()
console.info('Created console')

# Load config file
config = {}
for config_file in os.listdir('config'):
    config.update(read_json_file('config/{0}'.format(config_file)))
    console.info('Loaded config file: {0}'.format(config_file))

# Make code easier to read with config variables
world_height = config['world']['height']
world_width = config['world']['width']
world_depth = config['world']['depth']

# Create screen
pygame.display.set_caption(config['screen']['title'] + config['game']['version'] if config['screen']['include_version_in_title'] else config['screen']['title'])
screen = pygame.display.set_mode([config['screen']['width'], config['screen']['height']])
console.info('Created screen')

# Create camera
camera = Camera()

# Load fonts
for i in config['fonts']:
    ff = pygame.font.Font('assets/fonts/{0}'.format(i['file']), int(i['size']))
    fonts[i['name']] = ff
    if i['default']:
        default_font = ff
console.info('Loaded fonts')

# Load tilesets
for i in config['tilesets']:
    ss = SpriteSheet('assets/tilesets/{0}'.format(i['file']), i['tile_width'], i['tile_height'])
    tilesets[i['name']] = ss
    if i['default']:
        default_tileset = ss
console.info('Loaded tilesets')

# Create text
infoTextObject = Text('Version {0}'.format(config['game']['version']), x=0, y=0)
console.info('Created text objects')

# Setup OpenSimplex
seed = uuid.uuid1().int >> 64
gen = OpenSimplex(seed=seed)
console.info('Using {0} as the seed'.format(seed))

# Generate world
for z in range(world_depth):
    zrow = []
    for y in range(world_height):
        row = []
        for x in range(world_width):
            v = int(gen.noise3d(
                x=x / (config['world']['generator']['freq'] * config['world']['generator']['octaves']),
                y=y / (config['world']['generator']['freq'] * config['world']['generator']['octaves']),
                z=z / (config['world']['generator']['freq'] * config['world']['generator']['octaves']) * config['world']['generator']['z-multiplier']) * 127.0 + 128.0)
            row.append(v)
        zrow.append(row)
    world.append(zrow)
console.info('Created world')

# Generate tile data
for z in range(world_depth):
    zrow = []
    for y in range(world_height):
        row = []
        for x in range(world_width):
            v = world[z][y][x]
            f = False
            for t in config['terrain']:
                if t['min'] <= abs(v) <= t['max']:
                    f = True
                    img = default_tileset.get_image(t['x'], t['y'])
                    row.append(Tile(name=t['name'], x=x, y=y, z=z, tangible=t['tangible'], image=img))
            if not f:
                console.warn('Could not find texture for tile at ({0}, {1})'.format(x, y))
        zrow.append(row)
    worldTiles.append(zrow)

# Spawn mobs
for z in range(world_depth):
    for y in range(world_height):
        for x in range(world_width):
            for mob in config['mobs']:
                if worldTiles[z][y][x].name in mob['spawn']:
                    if random.randint(0, 100 - mob['spawn'][worldTiles[z][y][x].name]) == 1:
                        worldEntities.append(entity_classes[mob['type']](name=mob['name'], x=x, y=y, z=z, health=mob['health'], tangible=mob['tangible'], image=default_tileset.get_image(mob['tilex'], mob['tiley'])))
console.info('Spawned mobs')

for z in range(world_depth):
    for y in range(world_height):
        for x in range(world_width):
            for tile_structure in config['tile_structures']:
                if tile_structure['random']['type'] == 'randint':
                    if random.randint(1, tile_structure['random']['range'] - tile_structure['random']['chance']) == 1:
                        if worldTiles[z][y][x].name in tile_structure['allowed_tiles']:
                            tile_structure_class = tile_structure_classes[tile_structure['name']]
                            tile_structure_object = tile_structure_class(
                                name=tile_structure['tile']['name'],
                                x=x,
                                y=y,
                                z=z,
                                tangible=tile_structure['tile']['tangible'],
                                image=ss.get_image(tile_structure['tile']['image']['x'],
                                                   tile_structure['tile']['image']['y']
                                ),
                            )

                            tile_structure_object.setup()
                            worldTiles[z][y][x] = tile_structure_object
# Generate start position
px = random.randint(0, world_width-1)
py = random.randint(0, world_height-1)
while worldTiles[world_depth - 1][py][px].tangible:
    px = random.randint(0, world_width-1)
    py = random.randint(0, world_height-1)

console.info('Generated player spawn')

# Create player
player = Player(
    x=px,
    y=py,
    z=world_depth - 1,
    image=ss.get_image(config['player']['image']['x'], config['player']['image']['y']),
    exp=0,
    selected_item=None,
    inventory=[
        ItemSword,
        ItemHammer
    ],

    stats=StatsObject(
        health=20,
        strength=5,
        intelligence=5,
        agility=5,
        dexterity=5
    )
)
console.info('Created player')

# Create menus
menus.append(
    Menu(
        name='game',
        title='Game',
        items=[
            MenuItem('Quit', quit_game),
            MenuItem('Restart', restart_game),
            MenuItem('About', open_help, {'page': 'about', 'title': 'About ExploreGame'})
        ],
        x=10,
        y=10,
        toggle_key = pygame.K_m
    )
)

menus.append(
    Menu(
        name='inventory',
        title='Inventory',
        items=get_inventory_menuitems(),
        x=10,
        y=10,
        toggle_key=pygame.K_i
    )
)

# Set item icons
for item in items:
    item.icon = ss.get_image(config['items'][item.id]['icon']['x'], config['items'][item.id]['icon']['y'])
item_icon = Item.icon
console.info('Loaded icons for items')

# Main loop
while True:

    # Update info text
    infoTextObject.set_text('{0} ({1}, {2}, {3}) {4}'.format(config['game']['version'], player.x, player.y, player.z, worldTiles[player.z][player.y][player.x].name))

    # Clear screen
    screen.fill((0, 0, 0))

    # Draw world
    worldSurface = pygame.Surface((world_width*32, world_height*32))
    for y in range(player.y - int(config['screen']['height'] / 32), player.y + int(config['screen']['height'] / 32) if world_height - player.y > int(config['screen']['height'] / 32) else world_height):
        for x in range(player.x - int(config['screen']['width'] / 32), player.x + int(config['screen']['width'] / 32) if world_width - player.x > int(config['screen']['width'] / 32) else world_width):
            v = worldTiles[player.z][y][x]
            worldSurface.blit(v.image, [v.x * 32, v.y * 32])

    for v in worldEntities:
        if v.health <= 0:
            worldEntities.remove(v)
        else:
            if player.z == v.z:
                worldSurface.blit(v.image, [v.x * 32, v.y * 32])

    tmpos = [config['screen']['width']/2+player.x*-32, config['screen']['height']/2+player.y*-32]
    screen.blit(worldSurface, tmpos)

    # Find entity in front of player
    target_entity = None
    target_entity_indicator = None
    for mob in worldEntities:
        if mob.z == player.z and mob.y == player.y - 1 and mob.x == player.x:
            target_entity = mob
            target_entity_indicator = EntityInfoIndicator(target_entity)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # event is quit
            exit()
        elif event.type == pygame.KEYDOWN:
            if menu_open:
                if event.key == menu_open.toggle_key:
                    menu_open.close()
                else:
                    menu_open.handle_key(event.key)
            else:
                if event.key == pygame.K_ESCAPE:  # event is escape key
                    quit_game()
                elif event.key == pygame.K_UP:
                    tile = worldTiles[int(player.z)][int(player.y) - 1][int(player.x)]
                    if not tile.tangible and not check_entity_collision(player.x, player.y - 1, player.z):
                        player.y -= 1
                elif event.key == pygame.K_DOWN:
                    tile = worldTiles[int(player.z)][int(player.y) + 1][int(player.x)]
                    if not tile.tangible and not check_entity_collision(player.x, player.y + 1, player.z):
                        player.y += 1
                elif event.key == pygame.K_LEFT:
                    tile = worldTiles[int(player.z)][int(player.y)][int(player.x) - 1]
                    if not tile.tangible and not check_entity_collision(player.x - 1, player.y, player.z):
                        player.x -= 1
                elif event.key == pygame.K_RIGHT:
                    tile = worldTiles[int(player.z)][int(player.y)][int(player.x) + 1]
                    if not tile.tangible and not check_entity_collision(player.x + 1, player.y, player.z):
                        player.x += 1
                elif event.key == pygame.K_a:
                    if player.selected_item and target_entity:
                        player.selected_item.on_attack(self=player.selected_item, target=target_entity)

                if worldTiles[player.z][player.y][player.x].name == 'stairwell':
                    if worldTiles[player.z][player.y][player.x].stairwell_direction:
                        player.z += 1
                    else:
                        player.z -= 1
                for menu in menus:
                    if event.key == menu.toggle_key:
                        menu.toggle()

                if menu_open == None:
                    for v in worldEntities:
                        v.do_turn()

    # Draw objects
    if target_entity_indicator:
        target_entity_indicator.draw()

    infoTextObject.draw(screen)
    player.draw()

    if player.selected_item:
        screen.blit(player.selected_item.icon, [0, config['screen']['height'] - 32])

    # Draw menus
    for menu in menus:
        menu.draw(screen)

    # Flip the display
    pygame.display.flip()

