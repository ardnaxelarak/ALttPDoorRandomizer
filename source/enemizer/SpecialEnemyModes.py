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
                data[room_id][idx] = 'GreenMimic'
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

