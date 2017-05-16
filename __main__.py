from enum import Enum
import noise
import pygame
import random
import json
import os
import time

global menu_open
global item_icon

def main(args={}):
    # Globals
    global menu_open
    global item_icon

    # Init pygame
    pygame.init()

    # Variables
    fonts = {}
    tilesets = {}
    defaultFont = None
    defaultTileset = None
    world = []
    worldTiles = []
    cameraFollowsPlayer = True
    oldmap = []
    worldSurface = None
    worldEntities = []
    menus = []
    menu_open = None
    item_icon = None

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
        def __init__(self, name, image, x, y, health, tangible):
            self.name = name
            self.image = image
            self.x = x
            self.y = y
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
        id = "undefined"
        name = "undefined"
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
        def __init__(self, x, y, tx, ty, image, exp, stats, inventory, selected_item):
            self.xPos = x
            self.yPos = y
            self.xTile = tx
            self.yTile = ty
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

                if config['world']['height'] > self.y + dy > 0 and config['world'][
                    'width'] > self.x + dx > 0 and player.xTile != dx + self.x and player.yTile != dy + self.y:
                    if not worldTiles[self.y + dy][self.x + dx].tangible:
                        self.y += dy
                        self.x += dx
            except Exception as ex:
                console.warn("AnimalAI had a error: " + str(ex))

    # Fast Animal Entity class
    class FastAnimalEntity(Entity):
        def do_turn(self):
            try:
                dy = random.randint(-1, 1)
                dx = random.randint(-1, 1)

                if config['world']['height'] > self.y + dy > 0 and config['world'][
                    'width'] > self.x + dx > 0 and player.xTile != dx + self.x and player.yTile != dy + self.y:
                    if not worldTiles[self.y + dy][self.x + dx].tangible:
                        self.y += dy
                        self.x += dx
            except Exception as ex:
                console.warn("AnimalAI had a error: " + str(ex))

    # Tile class
    class Tile:
        def __init__(self, name, x, y, tangible, image):
            self.name = name
            self.x = x
            self.y = y
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
            hpY = config['indicators']['hp']['padding_top'] + config['indicators']['title']['padding_top'] + defaultFont.size(self.entity.name)[1]

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
        console.info("Selected inventory item {0}".format(item))
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
                    defaultFont.size(max(s, key=len))[0] + config['menu']['margin_left'] + config['menu'][
                        'margin_right'],
                    defaultFont.size(max(s, key=len))[1] * (len(items) + 1)
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

        def draw(self, targetSurface):
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
                            y=defaultFont.get_height() * (self.items.index(i) + 1) + config['menu']['margin_top'],
                            x=config['menu']['margin_left'])
                targetSurface.blit(self.surface, (self.x, self.y))

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

    """Begin Items"""

    class ItemSword(Item):
        id = "sword"
        name = "Sword"
        stats = ItemStats(attack=5)
        price = 5

    class ItemHammer(Item):
        id = "hammer"
        name = "Hammer"
        stats = ItemStats(attack=3, dexterity=2)
        price = 5

    """End items"""

    # Add items to classes
    items = [
        Item,
        ItemSword,
        ItemHammer
    ]

    # Entity config
    entity_types = {
        "animal": AnimalEntity,
        "fast_animal": FastAnimalEntity
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

    # Entity collision function
    def check_entity_collision(x, y):
        for i in worldEntities:
            if i.x == x and i.y == y and i.tangible:
                return True
        return False

    # Get inventory items function
    def get_inventory_menuitems():
        o = []
        for i in player.inventory:
            o.append(MenuItem(text=i.name, action=select_inventory_item, args={"item": i}))
        return o

    # Load config file
    config = read_json_file('config.json')

    # Create console
    console = Console()
    console.info('Created console')

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
            defaultFont = ff
    console.info('Loaded fonts')

    # Load tilesets
    for i in config['tilesets']:
        ss = SpriteSheet('assets/tilesets/{0}'.format(i['file']), i['tile_width'], i['tile_height'])
        tilesets[i['name']] = ss
        if i['default']:
            defaultTileset = ss
    console.info('Loaded tilesets')

    # Create text
    infoTextObject = Text('Version {0}'.format(config['game']['version']), x=0, y=0)
    console.info('Created text objects')

    # Generate world
    for y in range(config['world']['height']):
        row = []
        for x in range(config['world']['width']):
            v = int(noise.pnoise2(x / (config['world']['generator']['freq'] * config['world']['generator']['octaves']),
                                         y / (config['world']['generator']['freq'] * config['world']['generator']['octaves']),
                                         config['world']['generator']['octaves']) * 127.0 + 128.0)
            row.append(v)
        world.append(row)
    console.info('Created world')

    # Generate tile data
    for y in range(config['world']['height']):
        row = []
        for x in range(config['world']['width']):
            v = world[y][x]
            f = False
            for t in config['terrain']:
                if t['min'] <= abs(v) <= t['max']:
                    f = True
                    img = defaultTileset.get_image(t['x'], t['y'])
                    row.append(Tile(name=t['name'], x=x, y=y, tangible=t['tangible'], image=img))
            if not f:
                console.warn('Could not find texture for tile at ({0}, {1})'.format(x, y))
        worldTiles.append(row)

    # Spawn mobs
    for y in range(config['world']['height']):
        for x in range(config['world']['width']):
            for mob in config['mobs']:
                if worldTiles[y][x].name in mob['spawn']:
                    if random.randint(0, 100 - mob['spawn'][worldTiles[y][x].name]) == 1:
                        worldEntities.append(entity_types[mob['type']](name=mob['name'], x=x, y=y, health=mob['health'], tangible=mob['tangible'], image=defaultTileset.get_image(mob['tilex'], mob['tiley'])))
    console.info('Spawned mobs')

    # Generate start position
    px = random.randint(0, config['world']['width']-1)
    py = random.randint(0, config['world']['height']-1)
    while worldTiles[py][px].tangible:
        px = random.randint(0, config['world']['width']-1)
        py = random.randint(0, config['world']['height']-1)

    console.info('Generated player spawn')

    # Create player
    player = Player(
        x=px*32,
        y=py*32,
        tx=px,
        ty=py,
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
            name="game",
            title="Game",
            items=[
                MenuItem("Quit", quit_game),
                MenuItem("Restart", main),
                MenuItem("About", main)
            ],
            x=10,
            y=10,
            toggle_key = pygame.K_m
        )
    )

    menus.append(
        Menu(
            name="inventory",
            title="Inventory",
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
    console.info("Loaded icons for items")

    # Main loop
    while True:

        # Update info text
        infoTextObject.set_text('{0} ({1}, {2}) {3}'.format(config['game']['version'], player.xTile, player.yTile, worldTiles[player.yTile][player.xTile].name))

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw world
        worldSurface = pygame.Surface((config['world']['width']*32, config['world']['height']*32))
        for y in range(config['world']['height']):
            for x in range(config['world']['width']):
                v = worldTiles[y][x]
                worldSurface.blit(v.image, [v.x * 32, v.y * 32])

        for v in worldEntities:
            if v.health <= 0:
                worldEntities.remove(v)
            else:
                worldSurface.blit(v.image, [v.x * 32, v.y * 32])
        tmpos = [config['screen']['width']/2+player.xTile*-32, config['screen']['height']/2+player.yTile*-32]
        screen.blit(worldSurface, tmpos)

        # Find entity in front of player
        target_entity = None
        target_entity_indicator = None
        for mob in worldEntities:
            if mob.x == player.xTile and mob.y == player.yTile - 1:
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
                        tile = worldTiles[int(player.yTile) - 1][int(player.xTile)]
                        if not tile.tangible and not check_entity_collision(player.xTile, player.yTile - 1):
                            player.yPos -= 32
                            player.yTile -= 1
                    elif event.key == pygame.K_DOWN:
                        tile = worldTiles[int(player.yTile) + 1][int(player.xTile)]
                        if not tile.tangible and not check_entity_collision(player.xTile, player.yTile + 1):
                            player.yPos += 32
                            player.yTile += 1
                    elif event.key == pygame.K_LEFT:
                        tile = worldTiles[int(player.yTile)][int(player.xTile) - 1]
                        if not tile.tangible and not check_entity_collision(player.xTile - 1, player.yTile):
                            player.xPos -= 32
                            player.xTile -= 1
                    elif event.key == pygame.K_RIGHT:
                        tile = worldTiles[int(player.yTile)][int(player.xTile) + 1]
                        if not tile.tangible and not check_entity_collision(player.xTile + 1, player.yTile):
                            player.xPos += 32
                            player.xTile += 1
                    elif event.key == pygame.K_a:
                        if player.selected_item and target_entity:
                            player.selected_item.on_attack(self=player.selected_item, target=target_entity)
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

# Print message saying that the game is starting
print("[INFO] Starting game")

# Start the game
main()
