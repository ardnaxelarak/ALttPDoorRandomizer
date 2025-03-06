from collections import namedtuple
import logging
import RaceRandom as random

from BaseClasses import Region, RegionType, Shop, ShopType, Location
from Bosses import place_bosses
from Dungeons import get_dungeon_item_pool
from EntranceShuffle import connect_entrance
from Fill import FillError, fill_restrictive
from Items import ItemFactory


#This file sets the item pools for various modes. Timed modes and triforce hunt are enforced first, and then extra items are specified per mode to fill in the remaining space.
#Some basic items that various modes require are placed here, including pendants and crystals. Medallion requirements for the two relevant entrances are also decided.

alwaysitems = ['Bombos', 'Book of Mudora', 'Cane of Somaria', 'Ether', 'Fire Rod', 'Flippers', 'Ocarina', 'Hammer', 'Hookshot',
               'Ice Rod', 'Lamp', 'Cape', 'Magic Powder', 'Mushroom', 'Pegasus Boots', 'Quake', 'Shovel', 'Bug Catching Net',
               'Cane of Byrna', 'Blue Boomerang', 'Red Boomerang']
progressivegloves = ['Progressive Glove'] * 3

normalbottles = ['Bottle', 'Bottle (Red Potion)', 'Bottle (Green Potion)', 'Bottle (Blue Potion)', 'Bottle (Fairy)', 'Bottle (Bee)', 'Bottle (Good Bee)']
hardbottles = ['Bottle', 'Bottle (Red Potion)', 'Bottle (Green Potion)', 'Bottle (Blue Potion)', 'Bottle (Bee)', 'Bottle (Good Bee)']

normalbaseitems = (['Sanctuary Heart Container', 'Bombs (10)'] +
                   ['Rupees (300)'] * 4 + ['Boss Heart Container'] * 12 + ['Piece of Heart'] * 16)
expertbaseitems = (['Sanctuary Heart Container', 'Bombs (10)'] +
                   ['Rupees (300)'] * 4 + ['Boss Heart Container'] * 10 + ['Piece of Heart'] * 24)
normalfirst15extra = ['Rupees (100)', 'Rupees (300)', 'Rupees (50)'] + ['Bombs (3)'] * 6
normalsecond15extra = ['Bombs (3)'] * 10 + ['Rupees (50)'] * 2
normalthird10extra = ['Rupees (50)'] * 4 + ['Rupees (20)'] * 3
normalfourth5extra = ['Rupees (20)'] * 2
normalfinal25extra = ['Rupees (20)'] * 21

basecapacity = ['Bomb Upgrade (+10)'] + ['Arrow Upgrade (+10)'] * 3

Difficulty = namedtuple('Difficulty',
                        ['baseitems', 'bottles', 'bottle_count', 'same_bottle', 'progressiveshield',
                         'progressivearmor', 'swordless', 'magicitems',
                         'progressivesword', 'basicbow', 'teleporters',
                         'retro', 'extras', 'progressive_sword_limit', 'progressive_shield_limit',
                         'progressive_armor_limit', 'progressive_bottle_limit', 
                         'progressive_bow_limit', 'heart_piece_limit', 'boss_heart_container_limit'])

total_items_to_place = 153

difficulties = {
    'normal': Difficulty(
        baseitems = normalbaseitems,
        bottles = normalbottles,
        bottle_count = 4,
        same_bottle = False,
        progressiveshield = ['Progressive Shield'] * 3,
        progressivearmor = ['Progressive Armor'] * 2,
        swordless = ['Rupees (20)'] * 4,
        progressivesword = ['Progressive Sword'] * 3,
        basicbow = ['Bow', 'Silver Arrows'],
        magicitems = ['Bombos', 'Bombos', 'Cane of Somaria', 'Ether', 'Ether', 'Fire Rod', 'Ice Rod', 'Lamp', 'Cape', 'Cape',
                      'Quake', 'Quake', 'Cane of Byrna'],
        teleporters = 13,
        retro = ['Small Key (Universal)'] * 17 + ['Rupees (20)'] * 10,
        extras = [normalfirst15extra, normalsecond15extra, normalthird10extra, normalfourth5extra, normalfinal25extra],
        progressive_sword_limit = 4,
        progressive_shield_limit = 3,
        progressive_armor_limit = 2,
        progressive_bow_limit = 2,
        progressive_bottle_limit = 4,
        boss_heart_container_limit = 255,
        heart_piece_limit = 255,
    ),
    'hard': Difficulty(
        baseitems = normalbaseitems,
        bottles = hardbottles,
        bottle_count = 4,
        same_bottle = False,
        progressiveshield = ['Progressive Shield'] * 3,
        progressivearmor = ['Progressive Armor'] * 2,
        swordless =  ['Rupees (20)'] * 4,
        progressivesword =  ['Progressive Sword'] * 3,
        basicbow = ['Bow'] * 2,
        magicitems = ['Bombos', 'Cane of Somaria', 'Ether', 'Fire Rod', 'Ice Rod', 'Cape', 'Quake', 'Cane of Byrna'],
        teleporters = 18,
        retro = ['Small Key (Universal)'] * 12 + ['Rupees (5)'] * 15,
        extras = [normalfirst15extra, normalsecond15extra, normalthird10extra, normalfourth5extra, normalfinal25extra],
        progressive_sword_limit = 3,
        progressive_shield_limit = 2,
        progressive_armor_limit = 0,
        progressive_bow_limit = 1,
        progressive_bottle_limit = 4,
        boss_heart_container_limit = 6,
        heart_piece_limit = 16,
    ),
    'expert': Difficulty(
        baseitems = expertbaseitems,
        bottles = hardbottles,
        bottle_count = 4,
        same_bottle = False,
        progressiveshield = ['Progressive Shield'] * 3,
        progressivearmor = ['Progressive Armor'] * 2, # neither will count
        swordless = ['Rupees (20)'] * 4,
        progressivesword = ['Progressive Sword'] * 3,
        basicbow = ['Bow'] * 2,
        magicitems = [],
        teleporters = 20,
        retro = ['Small Key (Universal)'] * 12 + ['Rupees (5)'] * 15,
        extras = [normalfirst15extra, normalsecond15extra, normalthird10extra, normalfourth5extra, normalfinal25extra],
        progressive_sword_limit = 2,
        progressive_shield_limit = 1,
        progressive_armor_limit = 0,
        progressive_bow_limit = 1,
        progressive_bottle_limit = 4,
        boss_heart_container_limit = 2,
        heart_piece_limit = 8,
    ),
}

def generate_itempool(world, player):
    if (world.difficulty not in ['normal', 'hard', 'expert'] or world.goal not in ['ganon', 'pedestal', 'dungeons', 'crystals', 'all_items', 'completionist']
            or world.mode not in ['open', 'standard', 'inverted'] or world.timer not in ['none', 'ohko'] or world.progressive not in ['on', 'off', 'random']):
        raise NotImplementedError('Not supported yet')

    if world.timer in ['ohko', 'timed-ohko']:
        world.can_take_damage = False

    if world.goal in ['pedestal']:
        world.push_item(world.get_location('Ganon', player), ItemFactory('Nothing', player), False)
    else:
        world.push_item(world.get_location('Ganon', player), ItemFactory('Triforce', player), False)

    world.get_location('Ganon', player).event = True
    world.get_location('Ganon', player).locked = True
    world.push_item(world.get_location('Agahnim 1', player), ItemFactory('Beat Agahnim 1', player), False)
    world.get_location('Agahnim 1', player).event = True
    world.get_location('Agahnim 1', player).locked = True
    world.push_item(world.get_location('Agahnim 2', player), ItemFactory('Beat Agahnim 2', player), False)
    world.get_location('Agahnim 2', player).event = True
    world.get_location('Agahnim 2', player).locked = True
    world.push_item(world.get_location('Dark Blacksmith Ruins', player), ItemFactory('Pick Up Purple Chest', player), False)
    world.get_location('Dark Blacksmith Ruins', player).event = True
    world.get_location('Dark Blacksmith Ruins', player).locked = True
    world.push_item(world.get_location('Frog', player), ItemFactory('Get Frog', player), False)
    world.get_location('Frog', player).event = True
    world.get_location('Frog', player).locked = True
    world.push_item(world.get_location('Missing Smith', player), ItemFactory('Return Smith', player), False)
    world.get_location('Missing Smith', player).event = True
    world.get_location('Missing Smith', player).locked = True
    world.push_item(world.get_location('Floodgate', player), ItemFactory('Open Floodgate', player), False)
    world.get_location('Floodgate', player).event = True
    world.get_location('Floodgate', player).locked = True

    # set up item pool
    (pool, placed_items, precollected_items, clock_mode, treasure_hunt_count, treasure_hunt_icon, lamps_needed_for_dark_rooms) = get_pool_core(world.progressive, world.shuffle, world.difficulty, world.timer, world.goal, world.mode, world.swords, world.retro)
    world.itempool += ItemFactory(pool, player)
    for item in precollected_items:
        world.push_precollected(ItemFactory(item, player))
    for (location, item) in placed_items:
        world.push_item(world.get_location(location, player), ItemFactory(item, player), False)
        world.get_location(location, player).event = True
        world.get_location(location, player).locked = True
    world.lamps_needed_for_dark_rooms = lamps_needed_for_dark_rooms
    if clock_mode is not None:
        world.clock_mode = clock_mode
    if treasure_hunt_count is not None:
        world.treasure_hunt_count = treasure_hunt_count
    if treasure_hunt_icon is not None:
        world.treasure_hunt_icon = treasure_hunt_icon

    if world.keysanity:
        world.itempool.extend([item for item in get_dungeon_item_pool(world) if item.player == player])

    # logic has some branches where having 4 hearts is one possible requirement (of several alternatives)
    # rather than making all hearts/heart pieces progression items (which slows down generation considerably)
    # We mark one random heart container as an advancement item (or 4 heart pieces in expert mode)
    if world.difficulty in ['normal', 'hard']:
        [item for item in world.itempool if item.name == 'Boss Heart Container' and item.player == player][0].advancement = True
    elif world.difficulty in ['expert']:
        adv_heart_pieces = [item for item in world.itempool if item.name == 'Piece of Heart' and item.player == player][0:4]
        for hp in adv_heart_pieces:
            hp.advancement = True

    # mark only one copy of each magic item as advancement
    magic_items = ['Bombos', 'Cane of Somaria', 'Ether', 'Fire Rod', 'Ice Rod', 'Lamp', 'Cape', 'Quake', 'Cane of Byrna']
    for magic_item in magic_items:
        for extra_item in [item for item in world.itempool if item.name == magic_item and item.player == player][1:]:
            extra_item.advancement = False

    # shuffle medallions
    mm_medallion = ['Ether', 'Quake', 'Bombos'][random.randint(0, 2)]
    tr_medallion = ['Ether', 'Quake', 'Bombos'][random.randint(0, 2)]
    world.required_medallions[player] = (mm_medallion, tr_medallion)

    place_bosses(world, player)
    set_up_shops(world, player)

    if world.retro:
        set_up_take_anys(world, player)

    create_dynamic_shop_locations(world, player)

take_any_locations = [
    'Snitch Lady (East)', 'Snitch Lady (West)', 'Bush Covered House', 'Light World Bomb Hut',
    'Fortune Teller (Light)', 'Lake Hylia Fortune Teller', 'Lumberjack House', 'Bonk Fairy (Light)',
    'Bonk Fairy (Dark)', 'Lake Hylia Healer Fairy', 'Swamp Healer Fairy', 'Desert Healer Fairy',
    'Dark Lake Hylia Healer Fairy', 'Dark Lake Hylia Ledge Healer Fairy', 'Dark Desert Healer Fairy',
    'Dark Death Mountain Healer Fairy', 'Long Fairy Cave', 'Good Bee Cave', '20 Rupee Cave',
    'Kakariko Gamble Game', '50 Rupee Cave', 'Lost Woods Gamble', 'Hookshot Fairy',
    'Palace of Darkness Hint', 'East Dark World Hint', 'Archery Game', 'Dark Lake Hylia Ledge Hint',
    'Dark Lake Hylia Ledge Spike Cave', 'Fortune Teller (Dark)', 'Dark Sanctuary Hint', 'Dark Desert Hint']

def set_up_take_anys(world, player):
    if world.mode == 'inverted' and 'Dark Sanctuary Hint' in take_any_locations:
        take_any_locations.remove('Dark Sanctuary Hint')

    regions = random.sample(take_any_locations, 5)

    old_man_take_any = Region("Old Man Sword Cave", RegionType.Cave, 'the sword cave', player)
    world.regions.append(old_man_take_any)
    world.dynamic_regions.append(old_man_take_any)

    reg = regions.pop()
    entrance = world.get_region(reg, player).entrances[0]
    connect_entrance(world, entrance, old_man_take_any, player)
    entrance.target = 0x58
    old_man_take_any.shop = Shop(old_man_take_any, 0x0112, ShopType.TakeAny, 0xE2, True)
    world.shops.append(old_man_take_any.shop)
    old_man_take_any.shop.active = True

    swords = [item for item in world.itempool if item.type == 'Sword' and item.player == player]
    if swords:
        sword = random.choice(swords)
        world.itempool.remove(sword)
        world.itempool.append(ItemFactory('Rupees (20)', player))
        old_man_take_any.shop.add_inventory(0, sword.name, 0, 0, create_location=True)
    else:
        old_man_take_any.shop.add_inventory(0, 'Rupees (300)', 0, 0)

    for num in range(4):
        take_any = Region("Take-Any #{}".format(num+1), RegionType.Cave, 'a cave of choice', player)
        world.regions.append(take_any)
        world.dynamic_regions.append(take_any)

        target, room_id = random.choice([(0x58, 0x0112), (0x60, 0x010F), (0x46, 0x011F)])
        reg = regions.pop()
        entrance = world.get_region(reg, player).entrances[0]
        connect_entrance(world, entrance, take_any, player)
        entrance.target = target
        take_any.shop = Shop(take_any, room_id, ShopType.TakeAny, 0xE3, True)
        world.shops.append(take_any.shop)
        take_any.shop.active = True
        take_any.shop.add_inventory(0, 'Blue Potion', 0, 0)
        take_any.shop.add_inventory(1, 'Boss Heart Container', 0, 0)

    world.intialize_regions()

def create_dynamic_shop_locations(world, player):
    for shop in world.shops:
        if shop.region.player == player:
            for i, item in enumerate(shop.inventory):
                if item is None:
                    continue
                if item['create_location']:
                    loc = Location(player, "{} Item {}".format(shop.region.name, i+1), parent=shop.region)
                    shop.region.locations.append(loc)
                    world.dynamic_locations.append(loc)

                    world.clear_location_cache()

                    world.push_item(loc, ItemFactory(item['item'], player), False)
                    loc.event = True
                    loc.locked = True


def fill_prizes(world, attempts=15):
    all_state = world.get_all_state(keys=True)
    for player in range(1, world.players + 1):
        crystals = ItemFactory(['Red Pendant', 'Blue Pendant', 'Green Pendant', 'Crystal 1', 'Crystal 2', 'Crystal 3', 'Crystal 4', 'Crystal 7', 'Crystal 5', 'Crystal 6'], player)
        crystal_locations = [world.get_location('Turtle Rock - Prize', player), world.get_location('Eastern Palace - Prize', player), world.get_location('Desert Palace - Prize', player), world.get_location('Tower of Hera - Prize', player), world.get_location('Palace of Darkness - Prize', player),
                             world.get_location('Thieves\' Town - Prize', player), world.get_location('Skull Woods - Prize', player), world.get_location('Swamp Palace - Prize', player), world.get_location('Ice Palace - Prize', player),
                             world.get_location('Misery Mire - Prize', player)]
        placed_prizes = [loc.item.name for loc in crystal_locations if loc.item is not None]
        unplaced_prizes = [crystal for crystal in crystals if crystal.name not in placed_prizes]
        empty_crystal_locations = [loc for loc in crystal_locations if loc.item is None]

        for attempt in range(attempts):
            try:
                prizepool = list(unplaced_prizes)
                prize_locs = list(empty_crystal_locations)
                random.shuffle(prizepool)
                random.shuffle(prize_locs)
                fill_restrictive(world, all_state, prize_locs, prizepool)
            except FillError as e:
                logging.getLogger('').info("Failed to place dungeon prizes (%s). Will retry %s more times", e, attempts)
                for location in empty_crystal_locations:
                    location.item = None
                continue
            break
        else:
            raise FillError('Unable to place dungeon prizes')


def set_up_shops(world, player):
    # Changes to basic Shops
    # TODO: move hard+ mode changes for shields here, utilizing the new shops

    for shop in world.shops:
        shop.active = True

    if world.retro:
        rss = world.get_region('Red Shield Shop', player).shop
        rss.active = True
        rss.add_inventory(2, 'Single Arrow', 80)

    # Randomized changes to Shops
    if world.retro:
        for shop in random.sample([s for s in world.shops if s.replaceable and s.type == ShopType.Shop and s.region.player == player], 5):
            shop.active = True
            shop.add_inventory(0, 'Single Arrow', 80)
            shop.add_inventory(1, 'Small Key (Universal)', 100)
            shop.add_inventory(2, 'Bombs (10)', 50)

    #special shop types

def get_pool_core(progressive, shuffle, difficulty, timer, goal, mode, swords, retro):
    pool = []
    placed_items = []
    precollected_items = []
    clock_mode = None
    treasure_hunt_count = None
    treasure_hunt_icon = None

    pool.extend(alwaysitems)
    precollected_items.extend(basecapacity)

    def want_progressives():
        return random.choice([True, False]) if progressive == 'random' else progressive == 'on'

    pool.extend(progressivegloves)

    lamps_needed_for_dark_rooms = 1

    pool.extend(['Magic Mirror', 'Magic Mirror', 'Moon Pearl'])

    if timer == 'ohko':
        clock_mode = 'ohko'

    diff = difficulties[difficulty]
    pool.extend(diff.baseitems)
    pool.extend(diff.magicitems)

    # expert+ difficulties produce the same contents for
    # all bottles, since only one bottle is available
    if diff.same_bottle:
        thisbottle = random.choice(diff.bottles)
    for _ in range(diff.bottle_count):
        if not diff.same_bottle:
            thisbottle = random.choice(diff.bottles)
        pool.append(thisbottle)

    pool.extend(diff.progressiveshield)
    pool.extend(diff.progressivearmor)

    if swords != 'swordless':
        if want_progressives():
            pool.extend(['Progressive Bow'] * 2)
        else:
            pool.extend(diff.basicbow)

    if swords == 'swordless':
        pool.extend(diff.swordless)
        if want_progressives():
            pool.extend(['Progressive Bow'] * 2)
        else:
            pool.extend(['Bow', 'Silver Arrows'])
    elif swords == 'assured':
        precollected_items.append('Fighter Sword')
        pool.extend(diff.progressivesword)
        pool.extend(['Rupees (100)'])
    elif swords == 'vanilla':
        swords_to_use = []
        swords_to_use.extend(diff.progressivesword)
        swords_to_use.extend(['Progressive Sword'])
        random.shuffle(swords_to_use)

        placed_items.append(('Link\'s Uncle', swords_to_use.pop()))
        placed_items.append(('Blacksmith', swords_to_use.pop()))
        placed_items.append(('Pyramid Fairy - Left', swords_to_use.pop()))
        if goal != 'pedestal':
            placed_items.append(('Master Sword Pedestal', swords_to_use.pop()))
        else:
            placed_items.append(('Master Sword Pedestal', 'Triforce'))
    else:
        pool.extend(diff.progressivesword)
        pool.extend(['Progressive Sword'])

    extraitems = total_items_to_place - len(pool) - len(placed_items)

    pool.extend(['Teleporter'] * diff.teleporters)

    for extra in diff.extras:
        if extraitems > 0:
            pool.extend(extra)
            extraitems -= len(extra)

    if goal == 'pedestal' and swords != 'vanilla':
        placed_items.append(('Master Sword Pedestal', 'Triforce'))
    if retro:
        pool = [item.replace('Single Arrow','Rupees (5)') for item in pool]
        pool = [item.replace('Arrows (10)','Rupees (5)') for item in pool]
        pool = [item.replace('Arrow Upgrade (+5)','Rupees (5)') for item in pool]
        pool = [item.replace('Arrow Upgrade (+10)','Rupees (5)') for item in pool]
        pool.extend(diff.retro)
        if mode == 'standard':
            key_location = random.choice(['Secret Passage', 'Hyrule Castle - Boomerang Chest', 'Hyrule Castle - Map Chest', 'Hyrule Castle - Zelda\'s Chest', 'Sewers - Dark Cross'])
            placed_items.append((key_location, 'Small Key (Universal)'))
        else:
            pool.extend(['Small Key (Universal)'])
    return (pool, placed_items, precollected_items, clock_mode, treasure_hunt_count, treasure_hunt_icon, lamps_needed_for_dark_rooms)


# A quick test to ensure all combinations generate the correct amount of items.
def test():
    for difficulty in ['normal', 'hard', 'expert']:
        for goal in ['ganon', 'pedestal']:
            for timer in ['none', 'ohko']:
                for mode in ['open', 'standard', 'inverted']:
                    for swords in ['random', 'assured', 'swordless', 'vanilla']:
                        for progressive in ['on', 'off']:
                            for shuffle in ['full']:
                                for retro in [True, False]:
                                    out = get_pool_core(progressive, shuffle, difficulty, timer, goal, mode, swords, retro)
                                    count = len(out[0]) + len(out[1])

                                    correct_count = total_items_to_place
                                    if goal == 'pedestal' and swords != 'vanilla':
                                        # pedestal goals generate one extra item
                                        correct_count += 1
                                    if retro:
                                        correct_count += 28
                                    try:
                                        assert count == correct_count, "expected {0} items but found {1} items for {2}".format(correct_count, count, (progressive, shuffle, difficulty, timer, goal, mode, swords, retro))
                                    except AssertionError as e:
                                        print(e)

if __name__ == '__main__':
    test()
