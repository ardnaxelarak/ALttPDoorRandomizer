import RaceRandom as random
from Utils import snes_to_pc

from source.dungeon.EnemyList import EnemySprite, SpriteType, sprite_translation, enemy_names

def can_combine_req(req1, req2):
    for i in range(0, 4):
        if req1.sub_groups[i] and req2.sub_groups[i]:
            if len(set(req1.sub_groups[i]).intersection(req2.sub_groups[i])) == 0:
                return False
    return True

def get_enemy_map(mode, reqs, vanilla_map):
    data = {}

    if mode != "mimics":
        return data

    green_mimic = reqs.get((EnemySprite.GreenMimic, 0))

    for room_id, sprites in vanilla_map.items():
        data[room_id] = {}
        for idx, sprite in enumerate(sprites):
            subtype = 0 if sprite.sub_type != SpriteType.Overlord else sprite.sub_type
            req = reqs.get((sprite.kind, subtype))
            if not req or isinstance(req, dict) or req.boss:
                continue
            if req.static:
                if not can_combine_req(green_mimic, req):
                    data[room_id] = {}
                    break
                continue
            if req.killable:
                if random.random() > 0.1:
                    data[room_id][idx] = 'GreenMimic'
                else:
                    data[room_id][idx] = 'RedMimic'
            else:
                data[room_id][idx] = enemy_names[sprite.kind]
        if len(data[room_id]) == 0:
            del data[room_id]
    return data


def get_enemy_map_ow(mode, data_tables):
    reqs = data_tables.sprite_requirements
    return get_enemy_map(mode, reqs, data_tables.ow_enemy_table)

def get_enemy_map_uw(mode, data_tables):
    reqs = data_tables.sprite_requirements
    return get_enemy_map(mode, reqs, data_tables.uw_enemy_table.room_map)

def write_mimic_changes(rom, double = False):
    if double:
        rom.write_bytes(snes_to_pc(0x1EC71B),
           [0x00, 0xE0, 0x20, 0x00, 0x00, 0xE6, 0x1A, 0x00,
            0x00, 0xE6, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0xD0, 0x30, 0x00, 0x00, 0xE0, 0x20, 0x00,
            0x00, 0xE0, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,

            0x00, 0x00, 0x00, 0x00, 0xE0, 0xF6, 0xF6, 0x00,
            0x20, 0x1A, 0x1A, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0xD0, 0xE0, 0xE0,
            0x30, 0x20, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00])
    else:
        rom.write_bytes(snes_to_pc(0x1EC71B),
           [0x00, 0xF0, 0x10, 0x00, 0x00, 0xF3, 0x0D, 0x00,
            0x00, 0xF3, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(snes_to_pc(0x1EC75C), [0x01, 0x00])
    # rom.write_byte(snes_to_pc(0x0DB3DD), 0x0D) # make red mimics use green palette

