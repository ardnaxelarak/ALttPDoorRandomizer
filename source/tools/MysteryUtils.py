import argparse
import RaceRandom as random
import os
from pathlib import Path

import urllib.request
import urllib.parse
import yaml


def get_weights(path):
    if os.path.exists(Path(path)):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
    elif urllib.parse.urlparse(path).scheme in ['http', 'https']:
        return yaml.load(urllib.request.urlopen(path), Loader=yaml.FullLoader)

def roll_settings(weights):
    def get_choice(option, root=None):
        root = weights if root is None else root
        if option not in root:
            return None
        if type(root[option]) is not dict:
            return root[option]
        if not root[option]:
            return None
        return random.choices(list(root[option].keys()), weights=list(map(int, root[option].values())))[0]

    def get_choice_default(option, root=weights, default=None):
        choice = get_choice(option, root)
        if choice is None and default is not None:
            return default
        return choice

    while True:
        subweights = weights.get('subweights', {})
        if len(subweights) == 0:
            break
        chances = ({k: int(v['chance']) for (k, v) in subweights.items()})
        subweight_name = random.choices(list(chances.keys()), weights=list(chances.values()))[0]
        subweights = weights.get('subweights', {}).get(subweight_name, {}).get('weights', {})
        subweights['subweights'] = subweights.get('subweights', {})
        weights = {**weights, **subweights}

    ret = argparse.Namespace()

    ret.algorithm = get_choice('algorithm')

    glitch_map = {'none': 'noglitches', 'no_logic': 'nologic', 'owglitches': 'owglitches',
                  'owg': 'owglitches', 'minorglitches': 'minorglitches'}
    glitches_required = get_choice('glitches_required')
    if glitches_required is not None:
        if glitches_required not in glitch_map.keys():
            print(f'Logic did not match one of: {", ".join(glitch_map.keys())}')
            glitches_required = 'none'
        ret.logic = glitch_map[glitches_required]

    # item_placement = get_choice('item_placement')
    # not supported in ER

    dungeon_items = get_choice('dungeon_items')
    dungeon_items = '' if dungeon_items == 'standard' or dungeon_items is None else dungeon_items
    dungeon_items = 'mcsb' if dungeon_items == 'full' else dungeon_items
    ret.mapshuffle = get_choice('map_shuffle') == 'on' if 'map_shuffle' in weights else 'm' in dungeon_items
    ret.compassshuffle = get_choice('compass_shuffle') == 'on' if 'compass_shuffle' in weights else 'c' in dungeon_items
    if 'smallkey_shuffle' in weights:
        ret.keyshuffle = get_choice('smallkey_shuffle')
    else:
        if 's' in dungeon_items:
            ret.keyshuffle = 'wild'
        if 'u' in dungeon_items:
            ret.keyshuffle = 'universal'
    ret.bigkeyshuffle = get_choice('bigkey_shuffle') == 'on' if 'bigkey_shuffle' in weights else 'b' in dungeon_items

    ret.accessibility = get_choice('accessibility')
    ret.restrict_boss_items = get_choice('restrict_boss_items')

    overworld_shuffle = get_choice('overworld_shuffle')
    ret.ow_shuffle = overworld_shuffle if overworld_shuffle != 'none' else 'vanilla'
    ret.ow_terrain = get_choice('overworld_terrain') == 'on'
    valid_options = {'none', 'polar', 'grouped', 'limited', 'chaos'}
    ret.ow_crossed = get_choice('overworld_crossed')
    ret.ow_crossed = ret.ow_crossed if ret.ow_crossed in valid_options else 'none'
    ret.ow_keepsimilar = get_choice('overworld_keepsimilar') == 'on'
    ret.ow_mixed = get_choice('overworld_swap') == 'on'
    ret.ow_whirlpool = get_choice('whirlpool_shuffle') == 'on'
    overworld_flute = get_choice('flute_shuffle')
    ret.ow_fluteshuffle = overworld_flute if overworld_flute != 'none' else 'vanilla'
    ret.bonk_drops = get_choice('bonk_drops') == 'on'
    entrance_shuffle = get_choice('entrance_shuffle')
    ret.shuffle = entrance_shuffle if entrance_shuffle != 'none' else 'vanilla'
    overworld_map = get_choice('overworld_map')
    ret.overworld_map = overworld_map if overworld_map != 'default' else 'default'
    door_shuffle = get_choice('door_shuffle')
    ret.door_shuffle = door_shuffle if door_shuffle != 'none' else 'vanilla'
    ret.intensity = get_choice('intensity')
    ret.door_type_mode = get_choice('door_type_mode')
    ret.trap_door_mode = get_choice('trap_door_mode')
    ret.key_logic_algorithm = get_choice('key_logic_algorithm')
    ret.decoupledoors = get_choice('decoupledoors') == 'on'
    ret.experimental = get_choice('experimental') == 'on'
    ret.collection_rate = get_choice('collection_rate') == 'on'

    ret.dungeon_counters = get_choice('dungeon_counters') if 'dungeon_counters' in weights else 'default'
    if ret.dungeon_counters == 'default':
        ret.dungeon_counters = 'pickup' if ret.door_shuffle != 'vanilla' or ret.compassshuffle == 'on' else 'off'

    ret.pseudoboots = get_choice('pseudoboots') == 'on'
    ret.shopsanity = get_choice('shopsanity') == 'on'
    keydropshuffle = get_choice('keydropshuffle') == 'on'
    ret.dropshuffle = get_choice('dropshuffle') == 'on' or keydropshuffle
    ret.pottery = get_choice('pottery') if 'pottery' in weights else 'none'
    ret.pottery = 'keys' if ret.pottery == 'none' and keydropshuffle else ret.pottery
    ret.colorizepots = get_choice('colorizepots') == 'on'
    ret.shufflepots = get_choice('pot_shuffle') == 'on'
    ret.mixed_travel = get_choice('mixed_travel') if 'mixed_travel' in weights else 'prevent'
    ret.standardize_palettes = (get_choice('standardize_palettes') if 'standardize_palettes' in weights
                                else 'standardize')

    goal = get_choice('goals')
    if goal is not None:
        ret.goal = {'ganon': 'ganon',
                    'fast_ganon': 'crystals',
                    'dungeons': 'dungeons',
                    'pedestal': 'pedestal',
                    'triforce-hunt': 'triforcehunt',
                    'trinity': 'trinity',
                    'z1': 'z1',
                    'ganonhunt': 'ganonhunt',
                    'completionist': 'completionist'
                    }[goal]

    ret.openpyramid = get_choice('open_pyramid') if 'open_pyramid' in weights else 'auto'

    ret.shuffleganon = get_choice('shuffleganon') == 'on'
    ret.shufflelinks = get_choice('shufflelinks') == 'on'
    ret.shuffletavern = get_choice('shuffletavern') == 'on'

    ret.crystals_gt = get_choice('tower_open')
    ret.crystals_ganon = get_choice('ganon_open')

    ganon_item = get_choice('ganon_item')
    ret.ganon_item = ganon_item if ganon_item != 'none' else 'default'

    from ItemList import set_default_triforce
    default_tf_goal, default_tf_pool = set_default_triforce(ret.goal, 0, 0)
    goal_min = get_choice_default('triforce_goal_min', default=default_tf_goal)
    goal_max = get_choice_default('triforce_goal_max', default=default_tf_goal)
    pool_min = get_choice_default('triforce_pool_min', default=default_tf_pool)
    pool_max = get_choice_default('triforce_pool_max', default=default_tf_pool)
    ret.triforce_goal = random.randint(int(goal_min), int(goal_max))
    min_diff = get_choice_default('triforce_min_difference', default=(default_tf_pool-default_tf_goal))
    ret.triforce_pool = random.randint(max(int(pool_min), ret.triforce_goal + int(min_diff)), int(pool_max))

    ret.mode = get_choice('world_state')
    if ret.mode == 'retro':
        ret.mode = 'open'
        ret.retro = True
    ret.retro = get_choice('retro') == 'on'  # this overrides world_state if used
    ret.take_any = get_choice_default('take_any', default='none')

    ret.bombbag = get_choice('bombbag') == 'on'

    ret.hints = get_choice('hints') == 'on'

    swords = get_choice('weapons')
    if swords is not None:
        ret.swords = {'randomized': 'random',
                      'assured': 'assured',
                      'vanilla': 'vanilla',
                      'swordless': 'swordless',
                      'pseudo': 'pseudo',
                      'assured_pseudo': 'assured_pseudo',
                      'bombs': 'bombs',
                      'byrna': 'byrna',
                      'somaria': 'somaria',
                      'cane': 'cane',
                      'bees': 'bees',
                      'swordless_hammer': 'swordless_hammer'
                      }[swords]

    ret.difficulty = get_choice('item_pool')
    ret.flute_mode = get_choice_default('flute_mode', default='normal')
    ret.bow_mode = get_choice_default('bow_mode', default='progressive')

    ret.item_functionality = get_choice('item_functionality')

    old_style_bosses = {'basic': 'simple',
                        'normal': 'full',
                        'chaos': 'random'}
    boss_choice = get_choice('boss_shuffle')
    if boss_choice in old_style_bosses.keys():
        boss_choice = old_style_bosses[boss_choice]
    ret.shufflebosses = boss_choice

    enemy_choice = get_choice('enemy_shuffle')
    if enemy_choice == 'chaos':
        enemy_choice = 'random'
    ret.shuffleenemies = enemy_choice

    old_style_damage = {'none': 'default',
                        'chaos': 'random'}
    damage_choice = get_choice('enemy_damage')
    if damage_choice in old_style_damage:
        damage_choice = old_style_damage[damage_choice]
    ret.enemy_damage = damage_choice

    ret.enemy_health = get_choice('enemy_health')

    ret.beemizer = get_choice('beemizer') if 'beemizer' in weights else '0'

    inventoryweights = weights.get('startinventory', {})
    startitems = []
    for item in inventoryweights.keys():
        if get_choice(item, inventoryweights) == 'on':
            startitems.append(item)
    ret.startinventory = ','.join(startitems)
    if len(startitems) > 0:
        ret.usestartinventory = True

    if 'rom' in weights:
        romweights = weights['rom']
        ret.sprite = get_choice('sprite', romweights)
        ret.disablemusic = get_choice('disablemusic', romweights) == 'on'
        ret.quickswap = get_choice('quickswap', romweights) == 'on'
        ret.reduce_flashing = get_choice('reduce_flashing', romweights) == 'on'
        ret.msu_resume = get_choice('msu_resume', romweights) == 'on'
        ret.fastmenu = get_choice('menuspeed', romweights)
        ret.heartcolor = get_choice('heartcolor', romweights)
        ret.heartbeep = get_choice('heartbeep', romweights)
        ret.ow_palettes = get_choice('ow_palettes', romweights)
        ret.uw_palettes = get_choice('uw_palettes', romweights)
        ret.shuffle_sfx = get_choice('shuffle_sfx', romweights) == 'on'
        ret.msu_resume = get_choice('msu_resume', romweights) == 'on'

    return ret
