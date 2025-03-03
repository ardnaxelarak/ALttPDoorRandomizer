import itertools
import logging
from collections import defaultdict, deque

from BaseClasses import DoorType, dungeon_keys, KeyRuleType, RegionType
from Regions import dungeon_events
from Dungeons import dungeon_keys, dungeon_bigs, dungeon_table
from DungeonGenerator import ExplorationState, get_special_big_key_doors, count_locations_exclude_big_chest, prize_or_event
from DungeonGenerator import reserved_location, blind_boss_unavail


class KeyLayout(object):

    def __init__(self, sector, starts, proposal):
        self.sector = sector
        self.start_regions = starts
        self.event_starts = []
        self.proposal = proposal
        self.key_logic = KeyLogic(sector.name)

        self.key_counters = None
        self.flat_prop = None
        self.max_chests = None
        self.max_drops = None
        self.all_chest_locations = {}
        self.big_key_special = False
        self.all_locations = set()
        self.item_locations = set()

        self.found_doors = set()
        self.prize_relevant = None
        self.prize_can_lock = None  # if true, then you may need to beat the bo
        # bk special?
        # bk required? True if big chests or big doors exists

    def reset(self, proposal, builder, world, player):
        self.proposal = proposal
        self.flat_prop = flatten_pair_list(self.proposal)
        self.key_logic = KeyLogic(self.sector.name)
        self.max_chests = calc_max_chests(builder, self, world, player)
        self.all_locations = set()
        self.item_locations = set()
        self.prize_relevant = None


class KeyLogic(object):

    def __init__(self, dungeon_name):
        self.door_rules = {}
        self.bk_restricted = set()  # subset of free locations
        self.bk_locked = set()      # includes potentially other locations and key only locations
        self.sm_restricted = set()
        self.small_key_name = dungeon_keys[dungeon_name]
        self.bk_name = dungeon_bigs[dungeon_name]
        self.bk_doors = set()
        self.bk_chests = set()
        self.logic_min = {}
        self.logic_max = {}
        self.placement_rules = []
        self.location_rules = {}
        self.outside_keys = 0
        self.outside_keys_locations = set()
        self.dungeon = dungeon_name
        self.sm_doors = {}
        self.prize_location = None

    def check_placement(self, unplaced_keys, wild_keys, reached_keys, self_locking_keys,
                        big_key_loc=None, prize_loc=None, cr_count=7):
        for rule in self.placement_rules:
            if not rule.is_satisfiable(self.outside_keys_locations, wild_keys, reached_keys, self_locking_keys,
                                       unplaced_keys, big_key_loc, prize_loc, cr_count):
                return False
            if big_key_loc:
                for rule_a, rule_b in itertools.combinations(self.placement_rules, 2):
                    if rule_a.contradicts(rule_b, unplaced_keys, big_key_loc):
                        return False
        return True

    def reset(self):
        self.door_rules.clear()
        self.bk_restricted.clear()
        self.bk_locked.clear()
        self.sm_restricted.clear()
        self.bk_doors.clear()
        self.bk_chests.clear()
        self.placement_rules.clear()


class DoorRules(object):

    def __init__(self, number, is_valid):
        self.small_key_num = number
        self.is_valid = is_valid
        # allowing a different number if bk is behind this door in a set of locations
        self.alternate_small_key = None
        self.alternate_big_key_loc = set()
        # for a place with only 1 free location/key_only_location behind it ... no goals and locations
        self.allow_small = False
        self.small_location = None
        self.opposite = None

        self.new_rules = {}  # keyed by type, or type+lock_item -> number


class LocationRule(object):
    def __init__(self):
        self.small_key_num = 0
        self.conditional_sets = []


class ConditionalLocationRule(object):
    def __init__(self, conditional_set):
        self.conditional_set = conditional_set
        self.small_key_num = 0


class PlacementRule(object):

    def __init__(self):
        self.door_reference = None
        self.small_key = None
        self.bk_conditional_set = None  # the location that means
        self.needed_keys_w_bk = None
        self.needed_keys_wo_bk = None
        self.check_locations_w_bk = None
        self.special_bk_avail = False
        self.check_locations_wo_bk = None
        self.bk_relevant = True
        self.key_reduced = False
        self.prize_relevance = None

    def contradicts(self, rule, unplaced_keys, big_key_loc):
        bk_blocked = big_key_loc in self.bk_conditional_set if self.bk_conditional_set else False
        rule_blocked = big_key_loc in rule.bk_conditional_set if rule.bk_conditional_set else False
        check_locations = self.check_locations_wo_bk if bk_blocked else self.check_locations_w_bk
        rule_locations = rule.check_locations_wo_bk if rule_blocked else rule.check_locations_w_bk
        if check_locations is None or rule_locations is None:
            return False
        if not bk_blocked and big_key_loc not in check_locations:  # bk is not available, so rule doesn't apply
            return False
        if not rule_blocked and big_key_loc not in rule_locations:  # bk is not available, so rule doesn't apply
            return False
        check_locations = check_locations - {big_key_loc}
        rule_locations = rule_locations - {big_key_loc}
        threshold = self.needed_keys_wo_bk if bk_blocked else self.needed_keys_w_bk
        rule_threshold = rule.needed_keys_wo_bk if rule_blocked else rule.needed_keys_w_bk
        common_locations = rule_locations & check_locations
        shared = len(common_locations)
        if min(rule_threshold, threshold) - shared > 0:
            left = unplaced_keys - shared
            check_locations = check_locations - common_locations
            check_needed = threshold - shared
            if len(check_locations) < check_needed or left < check_needed:
                return True
            else:
                left -= check_needed
            rule_locations = rule_locations - common_locations
            rule_needed = rule_threshold - shared
            if len(rule_locations) < rule_needed or left < rule_needed:
                return True
            else:
                left -= rule_needed
        return False

    def is_satisfiable(self, outside_keys_locations, wild_keys, reached_keys, self_locking_keys, unplaced_keys,
                       big_key_loc, prize_location, cr_count):
        if self.prize_relevance and prize_location:
            if self.prize_relevance == 'BigBomb':
                 if prize_location.item.name not in ['Crystal 5', 'Crystal 6']:
                     return True
            elif self.prize_relevance == 'GT':
                if 'Crystal' not in prize_location.item.name or cr_count < 7:
                    return True
        bk_blocked = False
        if self.bk_conditional_set:
            for loc in self.bk_conditional_set:
                if loc.item and loc.item.bigkey:
                    bk_blocked = True
                    break
        elif len(self.check_locations_w_bk) > self.needed_keys_w_bk:
            def loc_has_bk(l):
                return (big_key_loc is not None and big_key_loc == l) or (l.item and l.item.bigkey)

            # todo: sometimes the bk avail rule doesn't mean the bk must be avail or this rule is invalid
            # but sometimes it certainly does
            # check threshold vs len(check_loc) maybe to determine bk isn't relevant?
            bk_found = self.special_bk_avail or any(loc for loc in self.check_locations_w_bk if loc_has_bk(loc))
            if not bk_found:
                return True
        check_locations = self.check_locations_wo_bk if bk_blocked else self.check_locations_w_bk
        if not bk_blocked and check_locations is None:
            return True
        available_keys = len(outside_keys_locations)
        # todo: sometimes we need an extra empty chest to accomodate the big key too
        # dungeon bias seed 563518200 for example
        threshold = self.needed_keys_wo_bk if bk_blocked else self.needed_keys_w_bk
        threshold -= self_locking_keys
        if not wild_keys:
            empty_chests = 0
            for loc in check_locations:
                if not loc.item:
                    empty_chests += 1
                elif loc.item and loc.item.name == self.small_key:
                    available_keys += 1
            place_able_keys = min(empty_chests, unplaced_keys)
            available_keys += place_able_keys
        else:
            available_keys += len(reached_keys.difference(outside_keys_locations))  # already placed small keys
            available_keys += unplaced_keys  # small keys not yet placed
        return available_keys >= threshold


class KeyCounter(object):

    def __init__(self, max_chests):
        self.max_chests = max_chests
        self.free_locations = {}
        self.key_only_locations = {}
        self.child_doors = {}
        self.open_doors = {}
        self.used_keys = 0
        self.big_key_opened = False
        self.important_location = False
        self.other_locations = {}
        self.important_locations = {}
        self.prize_doors_opened = False
        self.prize_received = False

    def used_smalls_loc(self, reserve=0):
        return max(self.used_keys + reserve - len(self.key_only_locations), 0)


def build_key_layout(builder, start_regions, proposal, event_starts, world, player):
    key_layout = KeyLayout(builder.master_sector, start_regions, proposal)
    key_layout.flat_prop = flatten_pair_list(key_layout.proposal)
    key_layout.max_drops = count_key_drops(key_layout.sector)
    key_layout.max_chests = calc_max_chests(builder, key_layout, world, player)
    key_layout.big_key_special = check_bk_special(key_layout.sector.region_set(), world, player)
    key_layout.all_locations = find_all_locations(key_layout.sector)
    key_layout.event_starts = list(event_starts.keys())
    return key_layout


def count_key_drops(sector):
    cnt = 0
    for region in sector.regions:
        for loc in region.locations:
            if loc.forced_item and 'Small Key' in loc.item.name:
                cnt += 1
    return cnt


def find_all_locations(sector):
    all_locations = set()
    for region in sector.regions:
        for loc in region.locations:
            all_locations.add(loc)
    return all_locations


def calc_max_chests(builder, key_layout, world, player):
    if world.doorShuffle[player] in ['basic', 'vanilla']:
        return len(world.get_dungeon(key_layout.sector.name, player).small_keys)
    return max(0, builder.key_doors_num - key_layout.max_drops)


def analyze_dungeon(key_layout, world, player):
    key_layout.key_logic.reset()
    key_layout.key_counters = create_key_counters(key_layout, world, player)
    key_logic = key_layout.key_logic
    for door in key_layout.proposal:
        if isinstance(door, tuple):
            key_logic.sm_doors[door[0]] = door[1]
            key_logic.sm_doors[door[1]] = door[0]
        else:
            if door.dest and door.type != DoorType.SpiralStairs:
                key_logic.sm_doors[door] = door.dest
                key_logic.sm_doors[door.dest] = door
            else:
                key_logic.sm_doors[door] = None

    find_bk_locked_sections(key_layout, world, player)
    key_logic.bk_chests.update(find_big_chest_locations(key_layout.all_chest_locations))
    key_logic.bk_chests.update(find_big_key_locked_locations(key_layout.all_chest_locations))
    key_logic.prize_location = dungeon_table[key_layout.sector.name].prize
    if world.keyshuffle[player] == 'universal' and world.mode[player] != 'standard':
        return

    original_key_counter = find_counter({}, False, key_layout, False)
    if key_layout.big_key_special and forced_big_key_avail(original_key_counter.other_locations) is not None:
        original_key_counter = find_counter({}, True, key_layout, False)
    queue = deque([(None, original_key_counter)])
    doors_completed = set()
    visited_cid = set()
    visited_cid.add(cid(original_key_counter, key_layout))

    while len(queue) > 0:
        queue = deque(sorted(queue, key=queue_sorter))
        parent_door, key_counter = queue.popleft()
        chest_keys = available_chest_small_keys(key_counter, world, player)
        raw_avail = chest_keys + len(key_counter.key_only_locations)
        available = raw_avail - key_counter.used_keys
        possible_smalls = count_unique_small_doors(key_counter, key_layout.flat_prop)
        avail_bigs = exist_relevant_big_doors(key_counter, key_layout) or exist_big_chest(key_counter)
        non_big_locs = count_locations_big_optional(key_counter.free_locations)
        big_avail = key_counter.big_key_opened or (key_layout.big_key_special and any(x for x in key_counter.other_locations.keys() if x.forced_item and x.forced_item.bigkey))
        if not big_avail:
            if chest_keys == non_big_locs and chest_keys > 0 and available <= possible_smalls and not avail_bigs:
                key_logic.bk_restricted.update(filter_big_chest(key_counter.free_locations))
            # note to self: this is due to the enough_small_locations function in validate_key_layout_sub_loop
            # I don't like this exception here or there
            # elif available < possible_smalls and avail_bigs and non_big_locs > 0:
            #     max_ctr = find_max_counter(key_layout)
            #     bk_lockdown = [x for x in max_ctr.free_locations if x not in key_counter.free_locations]
            #     key_logic.bk_restricted.update(filter_big_chest(bk_lockdown))
        # try to relax the rules here? - smallest requirement that doesn't force a softlock
        child_queue = deque()
        for child in key_counter.child_doors.keys():
            if can_open_door_by_counter(child, key_counter, key_layout, world, player):
                odd_counter = create_odd_key_counter(child, key_counter, key_layout, world, player)
                empty_flag = empty_counter(odd_counter)
                child_queue.append((child, odd_counter, empty_flag))
        while len(child_queue) > 0:
            child, odd_counter, empty_flag = child_queue.popleft()
            prize_flag = key_counter.prize_doors_opened
            if child in key_layout.flat_prop and child not in doors_completed:
                best_counter = find_best_counter(child, key_layout, odd_counter, False, empty_flag)
                rule = create_rule(best_counter, key_counter, world, player)
                create_worst_case_rule(rule, best_counter, world, player)
                check_for_self_lock_key(rule, child, best_counter, key_layout, world, player)
                bk_restricted_rules(rule, child, odd_counter, empty_flag, key_counter, key_layout, world, player)
                key_logic.door_rules[child.name] = rule
            elif not child.bigKey and child not in doors_completed:
                prize_flag = True
            doors_completed.add(child)
            next_counter = find_next_counter(child, key_counter, key_layout, prize_flag)
            ctr_id = cid(next_counter, key_layout)
            if ctr_id not in visited_cid:
                queue.append((child, next_counter))
                visited_cid.add(ctr_id)
    # todo: why is this commented out?
    # check_rules(original_key_counter, key_layout, world, player)

    # Flip bk rules if more restrictive, to prevent placing a big key in a softlocking location
    for rule in key_logic.door_rules.values():
        if rule.alternate_small_key is not None and rule.alternate_small_key > rule.small_key_num:
            max_counter = find_max_counter(key_layout)
            rule.alternate_big_key_loc = set(max_counter.free_locations.keys()).difference(rule.alternate_big_key_loc)
            rule.small_key_num, rule.alternate_small_key = rule.alternate_small_key, rule.small_key_num
    create_exhaustive_placement_rules(key_layout, world, player)
    set_paired_rules(key_logic, world, player)


def create_exhaustive_placement_rules(key_layout, world, player):
    key_logic = key_layout.key_logic
    max_ctr = find_max_counter(key_layout)
    for code, key_counter in key_layout.key_counters.items():
        if skip_key_counter_due_to_prize(key_layout, key_counter):
            continue  # we have the prize, we are not concerned about this case
        accessible_loc = set()
        accessible_loc.update(key_counter.free_locations)
        accessible_loc.update(key_counter.key_only_locations)
        blocked_loc = key_layout.item_locations.difference(accessible_loc)
        valid_rule = True
        # min_keys = max(count_unique_sm_doors(key_counter.child_doors), key_counter.used_keys + 1)
        min_keys = key_counter.used_keys + 1
        if len(blocked_loc) > 0 and len(key_counter.key_only_locations) < min_keys:
            rule = PlacementRule()
            rule.door_reference = code
            rule.small_key = key_logic.small_key_name
            if key_counter.big_key_opened or not big_key_progress(key_counter):
                rule.needed_keys_w_bk = min_keys
                rule.bk_relevant = key_counter.big_key_opened
                if key_counter.big_key_opened and rule.needed_keys_w_bk + 1 > len(accessible_loc):
                    valid_rule = False      # indicates that the big key cannot be in the accessible locations
                    key_logic.bk_restricted.update(accessible_loc.difference(max_ctr.key_only_locations))
                else:
                    placement_self_lock_adjustment(rule, max_ctr, blocked_loc, key_counter, world, player)
                    rule.check_locations_w_bk = accessible_loc
                    if key_layout.big_key_special:
                        rule.special_bk_avail = forced_big_key_avail(key_counter.important_locations) is not None
                    # check_sm_restriction_needed(key_layout, max_ctr, rule, blocked_loc)
            else:
                if big_key_progress(key_counter) and only_sm_doors(key_counter):
                    create_inclusive_rule(key_layout, max_ctr, code, key_counter, blocked_loc, accessible_loc, min_keys, world, player)
                rule.bk_conditional_set = blocked_loc
                rule.needed_keys_wo_bk = min_keys
                rule.check_locations_wo_bk = set(filter_big_chest(accessible_loc))
                rule.prize_relevance = key_layout.prize_relevant if rule_prize_relevant(key_counter) else None
            if valid_rule:
                key_logic.placement_rules.append(rule)
                adjust_locations_rules(key_logic, rule, accessible_loc, key_layout, key_counter, max_ctr)
    refine_placement_rules(key_layout, max_ctr)
    refine_location_rules(key_layout)


def rule_prize_relevant(key_counter):
    return not key_counter.prize_doors_opened and not key_counter.prize_received


def skip_key_counter_due_to_prize(key_layout, key_counter):
    return key_layout.prize_relevant and key_counter.prize_received and not key_counter.prize_doors_opened


def placement_self_lock_adjustment(rule, max_ctr, blocked_loc, ctr, world, player):
    if len(blocked_loc) == 1 and world.accessibility[player] != 'locations':
        blocked_others = set(max_ctr.other_locations).difference(set(ctr.other_locations))
        important_found = False
        for loc in blocked_others:
            if important_location(loc, world, player):
                important_found = True
                break
        if not important_found:
            rule.needed_keys_w_bk -= 1


# this rule is suspect - commented out usages for now
def check_sm_restriction_needed(key_layout, max_ctr, rule, blocked):
    if rule.needed_keys_w_bk == key_layout.max_chests + len(max_ctr.key_only_locations):
        key_layout.key_logic.sm_restricted.update(blocked.difference(max_ctr.key_only_locations))
        return True
    return False


def adjust_locations_rules(key_logic, rule, accessible_loc, key_layout, key_counter, max_ctr):
    if rule.bk_conditional_set:
        test_set = (rule.bk_conditional_set - key_logic.bk_locked) - set(max_ctr.key_only_locations.keys())
        needed = rule.needed_keys_wo_bk if test_set else 0
    else:
        test_set = None
        needed = rule.needed_keys_w_bk
    if needed > 0:
        all_accessible = set(accessible_loc)
        all_accessible.update(key_counter.other_locations)
        blocked_loc = key_layout.all_locations-all_accessible
        for location in blocked_loc:
            if location not in key_logic.location_rules.keys():
                loc_rule = LocationRule()
                key_logic.location_rules[location] = loc_rule
            else:
                loc_rule = key_logic.location_rules[location]
            if test_set:
                if location not in key_logic.bk_locked:
                    cond_rule = None
                    for other in loc_rule.conditional_sets:
                        if other.conditional_set == test_set:
                            cond_rule = other
                            break
                    if not cond_rule:
                        cond_rule = ConditionalLocationRule(test_set)
                        loc_rule.conditional_sets.append(cond_rule)
                    cond_rule.small_key_num = max(needed, cond_rule.small_key_num)
            else:
                loc_rule.small_key_num = max(needed, loc_rule.small_key_num)


def refine_placement_rules(key_layout, max_ctr):
    key_logic = key_layout.key_logic
    changed = True
    while changed:
        changed = False
        rules_to_remove = {}
        for rule in key_logic.placement_rules:
            if rule.check_locations_w_bk:
                rule.check_locations_w_bk.difference_update(key_logic.sm_restricted)
                key_onlys = rule.check_locations_w_bk.intersection(max_ctr.key_only_locations)
                if len(key_onlys) > 0:
                    rule.check_locations_w_bk.difference_update(key_onlys)
                    rule.needed_keys_w_bk -= len(key_onlys)
                if rule.needed_keys_w_bk == 0:
                    rules_to_remove[rule] = None
                # todo: evaluate this usage
                # if rule.bk_relevant and len(rule.check_locations_w_bk) == rule.needed_keys_w_bk + 1:
                #     new_restricted = set(max_ctr.free_locations) - rule.check_locations_w_bk
                #     if len(new_restricted | key_logic.bk_restricted) < len(key_layout.all_chest_locations):
                #         if len(new_restricted - key_logic.bk_restricted) > 0:
                #             key_logic.bk_restricted.update(new_restricted)  # bk must be in one of the check_locations
                #             changed = True
                #     else:
                #         rules_to_remove.append(rule)
                #         changed = True
                if rule.needed_keys_w_bk > key_layout.max_chests or len(rule.check_locations_w_bk) < rule.needed_keys_w_bk:
                    logging.getLogger('').warning('Invalid rule - what went wrong here??')
                    rules_to_remove[rule] = None
                    changed = True
            if rule.bk_conditional_set is not None:
                rule.bk_conditional_set.difference_update(key_logic.bk_restricted)
                rule.bk_conditional_set.difference_update(max_ctr.key_only_locations)
                if len(rule.bk_conditional_set) == 0:
                    rules_to_remove[rule] = None
            if rule.check_locations_wo_bk:
                rule.check_locations_wo_bk.difference_update(key_logic.sm_restricted)
                key_onlys = rule.check_locations_wo_bk.intersection(max_ctr.key_only_locations)
                if len(key_onlys) > 0:
                    rule.check_locations_wo_bk.difference_update(key_onlys)
                    rule.needed_keys_wo_bk -= len(key_onlys)
                if rule.needed_keys_wo_bk == 0:
                    rules_to_remove[rule] = None
                if len(rule.check_locations_wo_bk) < rule.needed_keys_wo_bk or rule.needed_keys_wo_bk > key_layout.max_chests:
                    if not rule.prize_relevance and len(rule.bk_conditional_set) > 0:
                        key_logic.bk_restricted.update(rule.bk_conditional_set)
                        rules_to_remove[rule] = None
                        changed = True  # impossible for bk to be here, I think
        for rule_a, rule_b in itertools.combinations([x for x in key_logic.placement_rules if x not in rules_to_remove], 2):
            if rule_b.bk_conditional_set and rule_a.check_locations_w_bk:
                temp = rule_a
                rule_a = rule_b
                rule_b = temp
            if rule_a.bk_conditional_set and rule_b.check_locations_w_bk:
                common_needed = min(rule_a.needed_keys_wo_bk, rule_b.needed_keys_w_bk)
                common_locs = len(rule_b.check_locations_w_bk & rule_a.check_locations_wo_bk)
                if (common_needed - common_locs) * 2 > key_layout.max_chests:
                    key_logic.bk_restricted.update(rule_a.bk_conditional_set)
                    rules_to_remove[rule_a] = None
                    changed = True
                    break
        equivalent_rules = []
        for rule in key_logic.placement_rules:
            for rule2 in key_logic.placement_rules:
                if rule != rule2 and rule not in rules_to_remove and rule2 not in rules_to_remove:
                    if rule.check_locations_w_bk and rule2.check_locations_w_bk:
                        if rule2.check_locations_w_bk == rule.check_locations_w_bk and rule2.needed_keys_w_bk > rule.needed_keys_w_bk:
                            rules_to_remove[rule] = None
                        elif rule2.needed_keys_w_bk == rule.needed_keys_w_bk and rule2.check_locations_w_bk < rule.check_locations_w_bk:
                            rules_to_remove[rule] = None
                        elif rule2.check_locations_w_bk == rule.check_locations_w_bk and rule2.needed_keys_w_bk == rule.needed_keys_w_bk:
                            equivalent_rules.append((rule, rule2))
                    if rule.check_locations_wo_bk and rule2.check_locations_wo_bk and rule.bk_conditional_set == rule2.bk_conditional_set:
                        if rule2.check_locations_wo_bk == rule.check_locations_wo_bk and rule2.needed_keys_wo_bk > rule.needed_keys_wo_bk:
                            rules_to_remove[rule] = None
                        elif rule2.needed_keys_wo_bk == rule.needed_keys_wo_bk and rule2.check_locations_wo_bk < rule.check_locations_wo_bk:
                            rules_to_remove[rule] = None
                        elif rule2.check_locations_wo_bk == rule.check_locations_wo_bk and rule2.needed_keys_wo_bk == rule.needed_keys_wo_bk:
                            equivalent_rules.append((rule, rule2))
        if len(rules_to_remove) > 0:
            key_logic.placement_rules = [x for x in key_logic.placement_rules if x not in rules_to_remove]
            equivalent_rules = [x for x in equivalent_rules if x[0] not in rules_to_remove and x[1] not in rules_to_remove]
        if len(equivalent_rules) > 0:
            removed_rules = {}
            for r1, r2 in equivalent_rules:
                if r1 in removed_rules.keys():
                    r1 = removed_rules[r1]
                if r2 in removed_rules.keys():
                    r2 = removed_rules[r2]
                if r1 != r2:
                    r1.door_reference += ','+r2.door_reference
                    key_logic.placement_rules.remove(r2)
                    removed_rules[r2] = r1


def refine_location_rules(key_layout):
    locs_to_remove = []
    for loc, rule in key_layout.key_logic.location_rules.items():
        conditions_to_remove = []
        for cond_rule in rule.conditional_sets:
            if cond_rule.small_key_num <= rule.small_key_num:
                conditions_to_remove.append(cond_rule)
        rule.conditional_sets = [x for x in rule.conditional_sets if x not in conditions_to_remove]
        if rule.small_key_num == 0 and len(rule.conditional_sets) == 0:
            locs_to_remove.append(loc)
    for loc in locs_to_remove:
        del key_layout.key_logic.location_rules[loc]


def create_inclusive_rule(key_layout, max_ctr, code, key_counter, blocked_loc, accessible_loc, min_keys, world, player):
    key_logic = key_layout.key_logic
    rule = PlacementRule()
    rule.door_reference = code
    rule.small_key = key_logic.small_key_name
    rule.needed_keys_w_bk = min_keys
    if key_counter.big_key_opened and rule.needed_keys_w_bk + 1 > len(accessible_loc):
        # indicates that the big key cannot be in the accessible locations
        key_logic.bk_restricted.update(accessible_loc.difference(max_ctr.key_only_locations))
    else:
        placement_self_lock_adjustment(rule, max_ctr, blocked_loc, key_counter, world, player)
        rule.check_locations_w_bk = accessible_loc
        # check_sm_restriction_needed(key_layout, max_ctr, rule, blocked_loc)
        key_logic.placement_rules.append(rule)
        adjust_locations_rules(key_logic, rule, accessible_loc, key_layout, key_counter, max_ctr)


def queue_sorter(queue_item):
    door, counter = queue_item
    if door is None:
        return 0
    return 1 if door.bigKey else 0


def queue_sorter_2(queue_item):
    door, counter, key_only = queue_item
    if door is None:
        return 0
    return 1 if door.bigKey else 0


def find_bk_locked_sections(key_layout, world, player):
    key_counters = key_layout.key_counters
    key_logic = key_layout.key_logic

    bk_not_required = set()
    big_chest_allowed_big_key = world.accessibility[player] != 'locations'
    for counter in key_counters.values():
        key_layout.all_chest_locations.update(counter.free_locations)
        key_layout.item_locations.update(counter.free_locations)
        key_layout.item_locations.update(counter.key_only_locations)
        key_layout.all_locations.update(key_layout.item_locations)
        key_layout.all_locations.update(counter.other_locations)
        if counter.big_key_opened and counter.important_location:
            big_chest_allowed_big_key = False
        if not counter.big_key_opened:
            bk_not_required.update(counter.free_locations)
            bk_not_required.update(counter.key_only_locations)
            bk_not_required.update(counter.other_locations)
    # todo?: handle bk special differently in cross dungeon
    # notably: things behind bk doors - relying on the bk door logic atm
    if not key_layout.big_key_special:
        key_logic.bk_restricted.update(dict.fromkeys(set(key_layout.all_chest_locations).difference(bk_not_required)))
        key_logic.bk_locked.update(dict.fromkeys(set(key_layout.all_locations) - bk_not_required))
    if not big_chest_allowed_big_key:
        bk_required_locations = find_big_chest_locations(key_layout.all_chest_locations)
        bk_required_locations += find_big_key_locked_locations(key_layout.all_chest_locations)
        key_logic.bk_restricted.update(bk_required_locations)
        key_logic.bk_locked.update(bk_required_locations)


def empty_counter(counter):
    if len(counter.key_only_locations) != 0 or len(counter.free_locations) != 0 or len(counter.child_doors) != 0:
        return False
    return not counter.important_location


def relative_empty_counter(odd_counter, key_counter):
    if len(set(odd_counter.key_only_locations).difference(key_counter.key_only_locations)) > 0:
        return False
    if len(set(odd_counter.free_locations).difference(key_counter.free_locations)) > 0:
        return False
    if len(set(odd_counter.other_locations).difference(key_counter.other_locations)) > 0:
        return False
    # important only
    if len(set(odd_counter.important_locations).difference(key_counter.important_locations)) > 0:
        return False
    new_child_door = False
    for child in odd_counter.child_doors:
        if unique_child_door(child, key_counter):
            new_child_door = True
            break
    if new_child_door:
        return False
    return True


def relative_empty_counter_2(odd_counter, key_counter):
    if len(set(odd_counter.key_only_locations).difference(key_counter.key_only_locations)) > 0:
        return False
    if len(set(odd_counter.free_locations).difference(key_counter.free_locations)) > 0:
        return False
    # important only
    if len(set(odd_counter.important_locations).difference(key_counter.important_locations)) > 0:
        return False
    for child in odd_counter.child_doors:
        if unique_child_door_2(child, key_counter):
            return False
    return True


def progressive_ctr(new_counter, last_counter):
    if len(set(new_counter.key_only_locations).difference(last_counter.key_only_locations)) > 0:
        return True
    if len(set(new_counter.free_locations).difference(last_counter.free_locations)) > 0:
        return True
    for child in new_counter.child_doors:
        if unique_child_door_2(child, last_counter):
            return True
    return False


def unique_child_door(child, key_counter):
    if child in key_counter.child_doors or child.dest in key_counter.child_doors:
        return False
    if child in key_counter.open_doors or child.dest in key_counter.open_doors:
        return False
    if child.bigKey and key_counter.big_key_opened:
        return False
    return True


def unique_child_door_2(child, key_counter):
    if child in key_counter.child_doors or child.dest in key_counter.child_doors:
        return False
    if child in key_counter.open_doors or child.dest in key_counter.open_doors:
        return False
    return True


# def find_best_counter(door, odd_counter, key_counter, key_layout, world, player, skip_bk, empty_flag):  # try to waste as many keys as possible?
#     ignored_doors = {door, door.dest} if door is not None else {}
#     finished = False
#     opened_doors = dict(key_counter.open_doors)
#     bk_opened = key_counter.big_key_opened
#     # new_counter = key_counter
#     last_counter = key_counter
#     while not finished:
#         door_set = find_potential_open_doors(last_counter, ignored_doors, key_layout, skip_bk)
#         if door_set is None or len(door_set) == 0:
#             finished = True
#             continue
#         for new_door in door_set:
#             proposed_doors = {**opened_doors, **dict.fromkeys([new_door, new_door.dest])}
#             bk_open = bk_opened or new_door.bigKey
#             new_counter = find_counter(proposed_doors, bk_open, key_layout)
#             bk_open = new_counter.big_key_opened
#             # this means the new_door invalidates the door / leads to the same stuff
#             if not empty_flag and relative_empty_counter(odd_counter, new_counter):
#                 ignored_doors.add(new_door)
#             elif empty_flag or key_wasted(new_door, door, last_counter, new_counter, key_layout, world, player):
#                 last_counter = new_counter
#                 opened_doors = proposed_doors
#                 bk_opened = bk_open
#             else:
#                 ignored_doors.add(new_door)
#     return last_counter


def find_best_counter(door, key_layout, odd_counter, skip_bk, empty_flag):
    best, best_ctr, locations = 0, None, 0
    for code, counter in key_layout.key_counters.items():
        if door not in counter.open_doors:
            if best_ctr is None or counter.used_keys > best or (counter.used_keys == best and count_locations(counter) > locations):
                if not skip_bk or not counter.big_key_opened:
                    if empty_flag or not relative_empty_counter(odd_counter, counter):
                        best = counter.used_keys
                        best_ctr = counter
                        locations = count_locations(counter)
    return best_ctr


def count_locations(ctr):
    return len(ctr.free_locations) + len(ctr.key_only_locations) + len(ctr.other_locations) + len(ctr.important_locations)


def find_worst_counter(door, odd_counter, key_counter, key_layout, skip_bk):  # try to waste as many keys as possible?
    ignored_doors = {door, door.dest} if door is not None else {}
    finished = False
    opened_doors = dict(key_counter.open_doors)
    bk_opened = key_counter.big_key_opened
    # new_counter = key_counter
    last_counter = key_counter
    while not finished:
        door_set = find_potential_open_doors(last_counter, ignored_doors, key_layout, skip_bk, 0)
        if door_set is None or len(door_set) == 0:
            finished = True
            continue
        for new_door in door_set:
            proposed_doors = {**opened_doors, **dict.fromkeys([new_door, new_door.dest])}
            bk_open = bk_opened or new_door.bigKey
            new_counter = find_counter(proposed_doors, bk_open, key_layout, key_counter.prize_doors_opened)
            bk_open = new_counter.big_key_opened
            if not new_door.bigKey and progressive_ctr(new_counter, last_counter) and relative_empty_counter_2(odd_counter, new_counter):
                ignored_doors.add(new_door)
            else:
                last_counter = new_counter
                opened_doors = proposed_doors
                bk_opened = bk_open
            # this means the new_door invalidates the door / leads to the same stuff
    return last_counter


def find_potential_open_doors(key_counter, ignored_doors, key_layout, skip_bk, reserve=1):
    small_doors = []
    big_doors = []
    if key_layout.big_key_special:
        big_key_available = any(x for x in key_counter.other_locations.keys() if x.forced_item and x.forced_item.bigkey)
    else:
        big_key_available = len(key_counter.free_locations) - key_counter.used_smalls_loc(reserve) > 0
    for other in key_counter.child_doors:
        if other not in ignored_doors and other.dest not in ignored_doors:
            if other.bigKey:
                if not skip_bk and (not key_layout.big_key_special or big_key_available):
                    big_doors.append(other)
            elif other.dest not in small_doors:
                small_doors.append(other)
    if len(small_doors) == 0 and (not skip_bk and (len(big_doors) == 0 or not big_key_available)):
        return None
    return small_doors + big_doors


def key_wasted(new_door, old_door, old_counter, new_counter, key_layout, world, player):
    if new_door.bigKey:  # big keys are not wastes - it uses up a location
        return True
    chest_keys = available_chest_small_keys(old_counter, world, player)
    old_key_diff = len(old_counter.key_only_locations) - old_counter.used_keys
    old_avail = chest_keys + old_key_diff
    new_chest_keys = available_chest_small_keys(new_counter, world, player)
    new_key_diff = len(new_counter.key_only_locations) - new_counter.used_keys
    new_avail = new_chest_keys + new_key_diff
    if new_key_diff < old_key_diff or new_avail < old_avail:
        return True
    if new_avail >= old_avail:
        wasted_keys = 0
        old_children = old_counter.child_doors.keys()
        new_children = [x for x in new_counter.child_doors.keys() if x != old_door and x.dest != old_door and (not x.bigKey or x not in old_children)]
        current_counter = new_counter
        opened_doors = dict(current_counter.open_doors)
        bk_opened = current_counter.big_key_opened
        for new_child in new_children:
            proposed_doors = {**opened_doors, **dict.fromkeys([new_child, new_child.dest])}
            bk_open = bk_opened or new_door.bigKey
            new_counter = find_counter(proposed_doors, bk_open, key_layout, current_counter.prize_doors_opened)
            if key_wasted(new_child, old_door, current_counter, new_counter, key_layout, world, player):
                wasted_keys += 1
            if new_avail - wasted_keys < old_avail:
                return True  # waste is possible
    return False


def find_next_counter(new_door, old_counter, key_layout, prize_flag=None):
    proposed_doors = {**old_counter.open_doors, **dict.fromkeys([new_door, new_door.dest])}
    bk_open = old_counter.big_key_opened or new_door.bigKey
    prize_flag = prize_flag if prize_flag else old_counter.prize_doors_opened
    return find_counter(proposed_doors, bk_open, key_layout, prize_flag)


def check_special_locations(locations):
    for loc in locations:
        if loc.name == 'Hyrule Castle - Zelda\'s Chest':
            return True
    return False


def calc_avail_keys(key_counter, world, player):
    chest_keys = available_chest_small_keys(key_counter, world, player)
    raw_avail = chest_keys + len(key_counter.key_only_locations)
    return raw_avail - key_counter.used_keys


def create_rule(key_counter, prev_counter, world, player):
    # prev_chest_keys = available_chest_small_keys(prev_counter, world)
    # prev_avail = prev_chest_keys + len(prev_counter.key_only_locations)
    chest_keys = available_chest_small_keys(key_counter, world, player)
    key_gain = len(key_counter.key_only_locations) - len(prev_counter.key_only_locations)
    # previous method
    # raw_avail = chest_keys + len(key_counter.key_only_locations)
    # available = raw_avail - key_counter.used_keys
    # possible_smalls = count_unique_small_doors(key_counter, key_layout.flat_prop)
    # required_keys = min(available, possible_smalls) + key_counter.used_keys
    required_keys = key_counter.used_keys + 1  # this makes more sense, if key_counter has wasted all keys
    adj_chest_keys = min(chest_keys, required_keys)
    needed_chests = required_keys - len(key_counter.key_only_locations)
    is_valid = needed_chests <= chest_keys
    unneeded_chests = min(key_gain, max(0, adj_chest_keys - needed_chests))
    rule_num = required_keys - unneeded_chests
    return DoorRules(rule_num, is_valid)


def create_worst_case_rule(rules, key_counter, world, player):
    required_keys = key_counter.used_keys + 1  # this makes more sense, if key_counter has wasted all keys
    rules.new_rules[KeyRuleType.WorstCase] = required_keys


def check_for_self_lock_key(rule, door, parent_counter, key_layout, world, player):
    if world.accessibility[player] != 'locations':
        counter = find_inverted_counter(door, parent_counter, key_layout, world, player)
        if not self_lock_possible(counter):
            return
        if len(counter.free_locations) == 1 and len(counter.key_only_locations) == 0 and not counter.important_location:
            rule.allow_small = True
            rule.small_location = next(iter(counter.free_locations))
            rule.new_rules[KeyRuleType.AllowSmall] = rule.new_rules[KeyRuleType.WorstCase] - 1


def find_inverted_counter(door, parent_counter, key_layout, world, player):
    # open all doors in counter
    counter = open_all_counter(parent_counter, key_layout, world, player, door=door)
    max_counter = find_max_counter(key_layout)
    # find the difference
    inverted_counter = KeyCounter(key_layout.max_chests)
    inverted_counter.free_locations = dict_difference(max_counter.free_locations, counter.free_locations)
    inverted_counter.key_only_locations = dict_difference(max_counter.key_only_locations, counter.key_only_locations)
    # child doors? used_keys?
    # inverted_counter.child_doors = dict_difference(max_counter.child_doors, counter.child_doors)
    inverted_counter.open_doors = dict_difference(max_counter.open_doors, counter.open_doors)
    inverted_counter.other_locations = dict_difference(max_counter.other_locations, counter.other_locations)
    for loc in inverted_counter.other_locations:
        if important_location(loc, world, player):
            inverted_counter.important_location = True
    return inverted_counter


def open_all_counter(parent_counter, key_layout, world, player, door=None, skipBk=False):
    changed = True
    counter = parent_counter
    proposed_doors = dict.fromkeys(parent_counter.open_doors.keys())
    while changed:
        changed = False
        doors_to_open = {}
        for child in counter.child_doors:
            if door is None or (child != door and child != door.dest):
                if skipBk:
                    if not child.bigKey:
                        doors_to_open[child] = None
                elif can_open_door_by_counter(child, counter, key_layout, world, player):
                    doors_to_open[child] = None
        if len(doors_to_open.keys()) > 0:
            proposed_doors = {**proposed_doors, **doors_to_open}
            bk_hint = counter.big_key_opened or any(d.bigKey for d in doors_to_open.keys())
            counter = find_counter(proposed_doors, bk_hint, key_layout, True)
            changed = True
    return counter


def open_some_counter(parent_counter, key_layout, ignored_doors):
    changed = True
    counter = parent_counter
    proposed_doors = dict.fromkeys(parent_counter.open_doors.keys())
    while changed:
        changed = False
        doors_to_open = {}
        for child in counter.child_doors:
            if child not in ignored_doors:
                if not child.bigKey:
                    doors_to_open[child] = None
        if len(doors_to_open.keys()) > 0:
            proposed_doors = {**proposed_doors, **doors_to_open}
            bk_hint = counter.big_key_opened
            for d in doors_to_open.keys():
                bk_hint = bk_hint or d.bigKey
            counter = find_counter(proposed_doors, bk_hint, key_layout, parent_counter.prize_doors_opened)
            changed = True
    return counter


def self_lock_possible(counter):
    return len(counter.free_locations) <= 1 and len(counter.key_only_locations) == 0 and not counter.important_location


def available_chest_small_keys(key_counter, world, player):
    if world.keyshuffle[player] == 'none':
        cnt = 0
        for loc in key_counter.free_locations:
            if key_counter.big_key_opened or '- Big Chest' not in loc.name:
                cnt += 1
        return min(cnt, key_counter.max_chests)
    else:
        return key_counter.max_chests


def available_chest_small_keys_logic(key_counter, world, player, sm_restricted):
    if world.keyshuffle[player] == 'none':
        cnt = 0
        for loc in key_counter.free_locations:
            if loc not in sm_restricted and (key_counter.big_key_opened or '- Big Chest' not in loc.name):
                cnt += 1
        return min(cnt, key_counter.max_chests)
    else:
        return key_counter.max_chests


def big_key_drop_available(key_counter):
    for loc in key_counter.other_locations:
        if loc.forced_big_key():
            return True
    return False


def bk_restricted_rules(rule, door, odd_counter, empty_flag, key_counter, key_layout, world, player):
    if key_counter.big_key_opened:
        return
    best_counter = find_best_counter(door, key_layout, odd_counter, True, empty_flag)
    bk_rule = create_rule(best_counter, key_counter, world, player)
    if bk_rule.small_key_num >= rule.small_key_num:
        return
    door_open = find_next_counter(door, best_counter, key_layout)
    ignored_doors = dict_intersection(best_counter.child_doors, door_open.child_doors)
    dest_ignored = []
    for d in ignored_doors.keys():
        if d.dest not in ignored_doors:
            dest_ignored.append(d.dest)
    ignored_doors = {**ignored_doors, **dict.fromkeys(dest_ignored)}
    post_counter = open_some_counter(door_open, key_layout, ignored_doors.keys())
    unique_loc = dict_difference(post_counter.free_locations, best_counter.free_locations)
    # todo: figure out the intention behind this change - better way to detect the big key is blocking needed key onlys?
    if len(unique_loc) > 0:  # and bk_rule.is_valid
        rule.alternate_small_key = bk_rule.small_key_num
        rule.alternate_big_key_loc.update(unique_loc)
        if not door.bigKey:
            rule.new_rules[(KeyRuleType.Lock, key_layout.key_logic.bk_name)] = best_counter.used_keys + 1


def find_worst_counter_wo_bk(small_key_num, accessible_set, door, odd_ctr, key_counter, key_layout):
    if key_counter.big_key_opened:
        return None, None, None
    worst_counter = find_worst_counter(door, odd_ctr, key_counter, key_layout, True)
    bk_rule_num = worst_counter.used_keys + 1
    bk_access_set = set()
    bk_access_set.update(worst_counter.free_locations)
    bk_access_set.update(worst_counter.key_only_locations)
    if bk_rule_num == small_key_num and len(bk_access_set ^ accessible_set) == 0:
        return None, None, None
    door_open = find_next_counter(door, worst_counter, key_layout)
    ignored_doors = dict_intersection(worst_counter.child_doors, door_open.child_doors)
    dest_ignored = []
    for door in ignored_doors.keys():
        if door.dest not in ignored_doors:
            dest_ignored.append(door.dest)
    ignored_doors = {**ignored_doors, **dict.fromkeys(dest_ignored)}
    post_counter = open_some_counter(door_open, key_layout, ignored_doors.keys())
    return worst_counter, post_counter, bk_rule_num


def open_a_door(door, child_state, flat_proposal, world, player):
    if door.bigKey or door.name in get_special_big_key_doors(world, player):
        child_state.big_key_opened = True
        child_state.avail_doors.extend(child_state.big_doors)
        child_state.opened_doors.extend(set([d.door for d in child_state.big_doors]))
        child_state.big_doors.clear()
    elif door in child_state.prize_door_set:
        child_state.prize_doors_opened = True
        for exp_door in child_state.prize_doors:
            new_region = exp_door.door.entrance.parent_region
            child_state.visit_region(new_region, key_checks=True)
            child_state.add_all_doors_check_keys(new_region, flat_proposal, world, player)
        child_state.prize_doors.clear()
    else:
        child_state.opened_doors.append(door)
        doors_to_open = [x for x in child_state.small_doors if x.door == door]
        child_state.small_doors[:] = [x for x in child_state.small_doors if x.door != door]
        child_state.avail_doors.extend(doors_to_open)
        dest_door = door.dest
        if dest_door in flat_proposal and door.type != DoorType.SpiralStairs:
            child_state.opened_doors.append(dest_door)
            if child_state.in_door_list_ic(dest_door, child_state.small_doors):
                now_available = [x for x in child_state.small_doors if x.door == dest_door]
                child_state.small_doors[:] = [x for x in child_state.small_doors if x.door != dest_door]
                child_state.avail_doors.extend(now_available)


# allows dest doors
def unique_doors(doors):
    unique_d_set = []
    for d in doors:
        if d.door not in unique_d_set:
            unique_d_set.append(d.door)
    return unique_d_set


# does not allow dest doors
def count_unique_sm_doors(doors):
    unique_d_set = set()
    for d in doors:
        if d not in unique_d_set and (d.dest not in unique_d_set or d.type == DoorType.SpiralStairs) and not d.bigKey:
            unique_d_set.add(d)
    return len(unique_d_set)


def big_key_progress(key_counter):
    return not only_sm_doors(key_counter) or exist_big_chest(key_counter)


def only_sm_doors(key_counter):
    for door in key_counter.child_doors:
        if door.bigKey:
            return False
    return True


# doesn't count dest doors
def count_unique_small_doors(key_counter, proposal):
    cnt = 0
    counted = set()
    for door in key_counter.child_doors:
        if door in proposal and door not in counted:
            cnt += 1
            counted.add(door)
            if door.type != DoorType.SpiralStairs:
                counted.add(door.dest)
    return cnt


def exist_relevant_big_doors(key_counter, key_layout):
    bk_counter = find_counter(key_counter.open_doors, True, key_layout, key_counter.prize_doors_opened, False)
    if bk_counter is not None:
        diff = dict_difference(bk_counter.free_locations, key_counter.free_locations)
        if len(diff) > 0:
            return True
        diff = dict_difference(bk_counter.key_only_locations, key_counter.key_only_locations)
        if len(diff) > 0:
            return True
        diff = dict_difference(bk_counter.child_doors, key_counter.child_doors)
        if len(diff) > 0:
            return True
    return False


def exist_big_chest(key_counter):
    for loc in key_counter.free_locations:
        if '- Big Chest' in loc.name:
            return True
    return False


def count_locations_big_optional(locations, bk=False):
    cnt = 0
    for loc in locations:
        if bk or '- Big Chest' not in loc.name:
            cnt += 1
    return cnt


def filter_big_chest(locations):
    return [x for x in locations if '- Big Chest' not in x.name]


def location_is_bk_locked(loc, key_logic):
    return loc in key_logic.bk_chests or loc in key_logic.bk_locked


# todo: verfiy this code is defunct
# def prize_or_event(loc):
#     return loc.name in dungeon_events or '- Prize' in loc.name or loc.name in ['Agahnim 1', 'Agahnim 2']
#
#
# def reserved_location(loc, world, player):
#     return loc in world.item_pool.config.reserved_locations[player]
#
#
# def blind_boss_unavail(loc, state, world, player):
#     if loc.name == "Thieves' Town - Boss":
#         return (loc.parent_region.dungeon.boss.name == 'Blind' and
#                 (not any(x for x in state.found_locations if x.name == 'Suspicious Maiden') or
#                  (world.get_region('Thieves Attic Window', player).dungeon.name == 'Thieves Town' and
#                   not any(x for x in state.found_locations if x.name == 'Attic Cracked Floor'))))
#     return False


# counts free locations for keys - hence why reserved locations don't count
def count_free_locations(state, world, player):
    cnt = 0
    for loc in state.found_locations:
        if (not prize_or_event(loc) and not loc.forced_item and not reserved_location(loc, world, player)
           and not blind_boss_unavail(loc, state.found_locations, world, player)):
            cnt += 1
    return cnt


def count_small_key_only_locations(state):
    cnt = 0
    for loc in state.found_locations:
        if loc.forced_item and loc.item.smallkey:
            cnt += 1
    return cnt


def big_chest_in_locations(locations):
    return len(find_big_chest_locations(locations)) > 0


def find_big_chest_locations(locations):
    ret = []
    for loc in locations:
        if 'Big Chest' in loc.name:
            ret.append(loc)
    return ret


def find_big_key_locked_locations(locations):
    ret = []
    for loc in locations:
        if loc.name in ["Thieves' Town - Blind's Cell", "Hyrule Castle - Zelda's Chest"]:
            ret.append(loc)
    return ret


def expand_key_state(state, flat_proposal, world, player):
    while len(state.avail_doors) > 0:
        exp_door = state.next_avail_door()
        door = exp_door.door
        connect_region = world.get_entrance(door.name, player).connected_region
        if state.validate(door, connect_region, world, player):
            state.visit_region(connect_region, key_checks=True)
            state.add_all_doors_check_keys(connect_region, flat_proposal, world, player)


def expand_big_key_state(state, flat_proposal, world, player):
    while len(state.avail_doors) > 0:
        exp_door = state.next_avail_door()
        door = exp_door.door
        connect_region = world.get_entrance(door.name, player).connected_region
        if state.validate(door, connect_region, world, player):
            state.visit_region(connect_region, key_checks=True)
            state.add_all_doors_check_big_keys(connect_region, flat_proposal, world, player)


def flatten_pair_list(paired_list):
    flat_list = []
    for d in paired_list:
        if type(d) is tuple:
            flat_list.append(d[0])
            flat_list.append(d[1])
        else:
            flat_list.append(d)
    return flat_list


def check_rules(original_counter, key_layout, world, player):
    all_key_only = set()
    key_only_map = {}
    queue = deque([(None, original_counter, original_counter.key_only_locations)])
    completed = set()
    completed.add(cid(original_counter, key_layout))
    while len(queue) > 0:
        queue = deque(sorted(queue, key=queue_sorter_2))
        access_door, counter, key_only_loc = queue.popleft()
        for loc in key_only_loc:
            if loc not in all_key_only:
                all_key_only.add(loc)
                access_rules = []
                key_only_map[loc] = access_rules
            else:
                access_rules = key_only_map[loc]
            if access_door is None or access_door.name not in key_layout.key_logic.door_rules.keys():
                if access_door is None or not access_door.bigKey:
                    access_rules.append(DoorRules(0, True))
            else:
                rule = key_layout.key_logic.door_rules[access_door.name]
                if rule not in access_rules:
                    access_rules.append(rule)
        for child in counter.child_doors.keys():
            if not child.bigKey or not key_layout.big_key_special or counter.big_key_opened:
                next_counter = find_next_counter(child, counter, key_layout)
                c_id = cid(next_counter, key_layout)
                if c_id not in completed:
                    completed.add(c_id)
                    new_key_only = dict_difference(next_counter.key_only_locations, counter.key_only_locations)
                    queue.append((child, next_counter, new_key_only))
    min_rule_bk = defaultdict(list)
    min_rule_non_bk = defaultdict(list)
    check_non_bk = False
    for loc, rule_list in key_only_map.items():
        m_bk = None
        m_nbk = None
        for rule in rule_list:
            if m_bk is None or rule.small_key_num <= m_bk:
                min_rule_bk[loc].append(rule)
                m_bk = rule.small_key_num
            if rule.alternate_small_key is None:
                ask = rule.small_key_num
            else:
                check_non_bk = True
                ask = rule.alternate_small_key
            if m_nbk is None or ask <= m_nbk:
                min_rule_non_bk[loc].append(rule)
                m_nbk = rule.alternate_small_key
    adjust_key_location_mins(key_layout, min_rule_bk, lambda r: r.small_key_num, lambda r, v: setattr(r, 'small_key_num', v))
    if check_non_bk:
        adjust_key_location_mins(key_layout, min_rule_non_bk, lambda r: r.small_key_num if r.alternate_small_key is None else r.alternate_small_key,
                                 lambda r, v: r if r.alternate_small_key is None else setattr(r, 'alternate_small_key', v))
    check_rules_deep(original_counter, key_layout, world, player)


def adjust_key_location_mins(key_layout, min_rules, getter, setter):
    collected_keys = key_layout.max_chests
    collected_locs = set()
    changed = True
    while changed:
        changed = False
        for_removal = []
        for loc, rules in min_rules.items():
            if loc in collected_locs:
                for_removal.append(loc)
            for rule in rules:
                if getter(rule) <= collected_keys and loc not in collected_locs:
                    changed = True
                    collected_keys += 1
                    collected_locs.add(loc)
                    for_removal.append(loc)
        for loc in for_removal:
            del min_rules[loc]
    if len(min_rules) > 0:
        for loc, rules in min_rules.items():
            for rule in rules:
                setter(rule, collected_keys)


def check_rules_deep(original_counter, key_layout, world, player):
    key_logic = key_layout.key_logic
    big_locations = {x for x in key_layout.all_chest_locations if x not in key_logic.bk_restricted}
    queue = deque([original_counter])
    completed = set()
    completed.add(cid(original_counter, key_layout))
    last_counter = None
    bail = 0
    while len(queue) > 0:
        counter = queue.popleft()
        if counter == last_counter:
            bail += 1
            if bail > 10:
                raise Exception('Key logic issue, during deep rule check: %s' % key_layout.sector.name)
        else:
            bail = 0
        last_counter = counter
        chest_keys = available_chest_small_keys_logic(counter, world, player, key_logic.sm_restricted)
        bk_drop = big_key_drop_available(counter)
        big_avail = counter.big_key_opened or bk_drop
        big_maybe_not_found = not counter.big_key_opened and not bk_drop  # better named as big_missing?
        if not key_layout.big_key_special and not big_avail:
            if world.bigkeyshuffle[player]:
                big_avail = True
            else:
                for location in counter.free_locations:
                    if location not in key_logic.bk_restricted:
                        big_avail = True
                        break
        outstanding_big_locs = {x for x in big_locations if x not in counter.free_locations}
        if big_maybe_not_found:
            if len(outstanding_big_locs) == 0 and not key_layout.big_key_special:
                big_maybe_not_found = False
        big_uses_chest = big_avail and not key_layout.big_key_special
        collected_alt = len(counter.key_only_locations) + chest_keys
        if big_uses_chest and chest_keys == count_locations_big_optional(counter.free_locations, counter.big_key_opened):
            chest_keys -= 1
        collected = len(counter.key_only_locations) + chest_keys
        can_progress = len(counter.child_doors) == 0
        smalls_opened, big_opened = False, False
        small_rules = []
        for door in counter.child_doors.keys():
            can_open = False
            if door.bigKey and big_avail:
                can_open = True
            elif door.name in key_logic.door_rules.keys():
                rule = key_logic.door_rules[door.name]
                small_rules.append(rule)
                if rule_satisfied(rule, collected, collected_alt, outstanding_big_locs, chest_keys, key_layout):
                    can_open = True
                    smalls_opened = True
            elif not door.bigKey:
                can_open = True
            if can_open:
                can_progress = (big_avail or not big_maybe_not_found) if door.bigKey else smalls_opened
                next_counter = find_next_counter(door, counter, key_layout)
                c_id = cid(next_counter, key_layout)
                if c_id not in completed:
                    completed.add(c_id)
                    queue.append(next_counter)
        if not can_progress:
            if len(small_rules) > 0:  # zero could be indicative of a problem, but also, the big key is now required
                reduce_rules(small_rules, collected, collected_alt)
                queue.append(counter)  # run it through again
            else:
                raise Exception('Possible problem with generation or bk rules')


def rule_satisfied(rule, collected, collected_alt, outstanding_big_locs, chest_keys, key_layout):
    if collected >= rule.small_key_num:
        return True
    if rule.allow_small and collected >= rule.small_key_num-1 and chest_keys < key_layout.max_chests:
        return True
    rule_diff = outstanding_big_locs.difference(rule.alternate_big_key_loc)
    if rule.alternate_small_key is not None and len(rule_diff) == 0 and collected >= rule.alternate_small_key:
        return True
    if collected_alt > collected:
        if collected_alt >= rule.small_key_num:
            return True
        if rule.allow_small and collected_alt >= rule.small_key_num-1 and chest_keys+1 < key_layout.max_chests:
            return True
        if rule.alternate_small_key is not None and len(rule_diff) == 0 and collected_alt >= rule.alternate_small_key:
            return True
    return False


def reduce_rules(small_rules, collected, collected_alt):
    smallest_rules = []
    min_num = None
    for rule in small_rules:
        if min_num is None or rule.small_key_num <= min_num:
            if min_num is not None and rule.small_key_num < min_num:
                min_num = rule.small_key_num
                smallest_rules.clear()
            elif min_num is None:
                min_num = rule.small_key_num
            smallest_rules.append(rule)
    for rule in smallest_rules:
        if rule.allow_small:  # we are already reducing it
            rule.allow_small = False
        if min_num > collected_alt > collected:
            rule.small_key_num = collected_alt
        else:
            rule.small_key_num = collected


def set_paired_rules(key_logic, world, player):
    for d_name, rule in key_logic.door_rules.items():
        door = world.get_door(d_name, player)
        if door.dest.name in key_logic.door_rules.keys():
            rule.opposite = key_logic.door_rules[door.dest.name]


def check_bk_special(regions, world, player):
    for r_name in regions:
        region = world.get_region(r_name, player)
        for loc in region.locations:
            if loc.forced_big_key():
                return True
    return False


def forced_big_key_avail(locations):
    for loc in locations:
        if loc.forced_big_key():
            return loc
    return None


def prize_relevance(key_layout, dungeon_entrance, is_atgt_swapped):
    if len(key_layout.start_regions) > 1 and dungeon_entrance and dungeon_table[key_layout.key_logic.dungeon].prize:
        if dungeon_entrance.name == ('Agahnims Tower' if is_atgt_swapped else 'Ganons Tower'):
            return 'GT'
        elif dungeon_entrance.name == 'Pyramid Fairy':
            return 'BigBomb'
    return None


def prize_relevance_sig2(start_regions, d_name, dungeon_entrance, is_atgt_swapped):
    if len(start_regions) > 1 and dungeon_entrance and dungeon_table[d_name].prize:
        if dungeon_entrance.name == ('Agahnims Tower' if is_atgt_swapped else 'Ganons Tower'):
            return 'GT'
        elif dungeon_entrance.name == 'Pyramid Fairy':
            return 'BigBomb'
    return None


def validate_bk_layout(proposal, builder, start_regions, world, player):
    bk_special = check_bk_special(builder.master_sector.regions, world, player)
    if world.bigkeyshuffle[player] and (world.dropshuffle[player] or not bk_special):
        return True
    flat_proposal = flatten_pair_list(proposal)
    state = ExplorationState(dungeon=builder.name)
    state.big_key_special = bk_special
    for region in start_regions:
        dungeon_entrance, portal_door = find_outside_connection(region)
        prize_relevant_flag = prize_relevance_sig2(start_regions, builder.name, dungeon_entrance, world.is_atgt_swapped(player))
        if prize_relevant_flag:
            state.append_door_to_list(portal_door, state.prize_doors)
            state.prize_door_set[portal_door] = dungeon_entrance
            # key_layout.prize_relevant = prize_relevant_flag
        else:
            state.visit_region(region, key_checks=True)
            state.add_all_doors_check_big_keys(region, flat_proposal, world, player)
    expand_big_key_state(state, flat_proposal, world, player)
    if bk_special:
        for loc in state.found_locations:
            if loc.forced_big_key():
                return True
    else:
        return state.count_locations_exclude_specials(world, player) > 0
    return False


# Soft lock stuff
def validate_key_layout(key_layout, world, player):
    # universal key is all good - except for hyrule castle in standard mode
    if world.logic[player] == 'nologic' or (world.keyshuffle[player] == 'universal' and
       (world.mode[player] != 'standard' or key_layout.sector.name != 'Hyrule Castle')):
        return True
    flat_proposal = key_layout.flat_prop
    state = ExplorationState(dungeon=key_layout.sector.name)
    state.init_zelda_event_doors(key_layout.event_starts, player)
    state.key_locations = key_layout.max_chests
    state.big_key_special = check_bk_special(key_layout.sector.regions, world, player)
    for region in key_layout.start_regions:
        dungeon_entrance, portal_door = find_outside_connection(region)
        prize_relevant_flag = prize_relevance(key_layout, dungeon_entrance, world.is_atgt_swapped(player))
        if prize_relevant_flag:
            state.append_door_to_list(portal_door, state.prize_doors)
            state.prize_door_set[portal_door] = dungeon_entrance
            key_layout.prize_relevant = prize_relevant_flag
        else:
            state.visit_region(region, key_checks=True)
            state.add_all_doors_check_keys(region, flat_proposal, world, player)
    return validate_key_layout_sub_loop(key_layout, state, {}, flat_proposal, None, 0, world, player)


def validate_key_layout_sub_loop(key_layout, state, checked_states, flat_proposal, prev_state, prev_avail, world, player):
    expand_key_state(state, flat_proposal, world, player)
    smalls_avail = len(state.small_doors) > 0   # de-dup crystal repeats
    num_bigs = 1 if len(state.big_doors) > 0 else 0  # all or nothing
    if not smalls_avail and num_bigs == 0:
        return True   # I think that's the end
    # todo: fix state to separate out these types
    if state.big_key_opened:
        ttl_locations = count_free_locations(state, world, player)
    else:
        ttl_locations = count_locations_exclude_big_chest(state.found_locations, world, player)
    ttl_small_key_only = count_small_key_only_locations(state)
    available_small_locations = cnt_avail_small_locations(ttl_locations, ttl_small_key_only, state,
                                                          key_layout, world, player)
    available_big_locations = cnt_avail_big_locations(ttl_locations, state, world, player)
    if invalid_self_locking_key(key_layout, state, prev_state, prev_avail, world, player):
        return False
    # todo: allow more key shuffles - refine placement rules
    # if (not smalls_avail or available_small_locations == 0) and (state.big_key_opened or num_bigs == 0 or available_big_locations == 0):
    found_forced_bk = state.found_forced_bk()
    smalls_done = not smalls_avail or available_small_locations == 0
    # or not enough_small_locations(state, available_small_locations)
    bk_done = state.big_key_opened or num_bigs == 0 or (available_big_locations == 0 and not found_forced_bk)
    # prize door should not be opened if the boss is reachable - but not reached yet
    allow_for_prize_lock = (key_layout.prize_can_lock and
                            not any(x for x in state.found_locations if '- Prize' in x.name))
    prize_done = not key_layout.prize_relevant or state.prize_doors_opened or allow_for_prize_lock
    if smalls_done and bk_done and prize_done:
        return False
    else:
        # todo: pretty sure you should OR these paths together, maybe when there's one location and it can
        # either be small or big key
        if smalls_avail and available_small_locations > 0:
            for exp_door in state.small_doors:
                state_copy = state.copy()
                open_a_door(exp_door.door, state_copy, flat_proposal, world, player)
                state_copy.used_smalls += 1
                if state_copy.used_smalls > ttl_small_key_only:
                    state_copy.used_locations += 1
                code = validate_id(state_copy, flat_proposal)
                if code not in checked_states.keys():
                    valid = validate_key_layout_sub_loop(key_layout, state_copy, checked_states, flat_proposal,
                                                         state, available_small_locations, world, player)
                    checked_states[code] = valid
                else:
                    valid = checked_states[code]
                if not valid:
                    return False
        if not state.big_key_opened and (available_big_locations >= num_bigs > 0 or (found_forced_bk and num_bigs > 0)):
            state_copy = state.copy()
            open_a_door(state.big_doors[0].door, state_copy, flat_proposal, world, player)
            if not found_forced_bk:
                state_copy.used_locations += 1
            code = validate_id(state_copy, flat_proposal)
            if code not in checked_states.keys():
                valid = validate_key_layout_sub_loop(key_layout, state_copy, checked_states, flat_proposal,
                                                     state, available_small_locations, world, player)
                checked_states[code] = valid
            else:
                valid = checked_states[code]
            if not valid:
                return False
        # todo: feel like you only open these if the boss is available???
        # todo: or if a crystal isn't valid placement on this boss
        if not state.prize_doors_opened and key_layout.prize_relevant:
            state_copy = state.copy()
            open_a_door(next(iter(state_copy.prize_door_set)), state_copy, flat_proposal, world, player)
            code = validate_id(state_copy, flat_proposal)
            if code not in checked_states.keys():
                valid = validate_key_layout_sub_loop(key_layout, state_copy, checked_states, flat_proposal,
                                                     state, available_small_locations, world, player)
                checked_states[code] = valid
            else:
                valid = checked_states[code]
            if not valid:
                return False
    return True


def invalid_self_locking_key(key_layout, state, prev_state, prev_avail, world, player):
    if prev_state is None or state.used_smalls == prev_state.used_smalls:
        return False
    if state.found_forced_bk() and not prev_state.found_forced_bk():
        return False
    if state.big_key_opened:
        new_bk_doors = set(state.big_doors).difference(set(prev_state.big_doors))
        state_copy = state.copy()
        while len(new_bk_doors) > 0:
            for door in new_bk_doors:
                open_a_door(door.door, state_copy, key_layout.flat_prop, world, player)
            new_bk_doors = set(state_copy.big_doors).difference(set(prev_state.big_doors))
        expand_key_state(state_copy, key_layout.flat_prop, world, player)
    else:
        state_copy = state
    new_locations = set(state_copy.found_locations).difference(set(prev_state.found_locations))
    important_found = False
    for loc in new_locations:
        important_found |= important_location(loc, world, player)
    if not important_found:
        return False
    new_small_doors = set(state.small_doors).difference(set(prev_state.small_doors))
    if len(new_small_doors) > 0:
        return False
    return prev_avail - 1 == 0


def enough_small_locations(state, avail_small_loc):
    unique_d_set = set()
    for exp_door in state.small_doors:
        door = exp_door.door
        if door not in unique_d_set and door.dest not in unique_d_set:
            unique_d_set.add(door)
    return avail_small_loc >= len(unique_d_set)


def determine_prize_lock(key_layout, world, player):
    if world.logic[player] == 'nologic' or (world.keyshuffle[player] == 'universal' and
       (world.mode[player] != 'standard' or key_layout.sector.name != 'Hyrule Castle')):
        return  # done, doesn't matter what
    flat_proposal = key_layout.flat_prop
    state = ExplorationState(dungeon=key_layout.sector.name)
    state.key_locations = key_layout.max_chests
    state.big_key_special = check_bk_special(key_layout.sector.regions, world, player)
    prize_lock_possible = False
    for region in key_layout.start_regions:
        dungeon_entrance, portal_door = find_outside_connection(region)
        prize_relevant_flag = prize_relevance(key_layout, dungeon_entrance, world.is_atgt_swapped(player))
        if prize_relevant_flag:
            state.append_door_to_list(portal_door, state.prize_doors)
            state.prize_door_set[portal_door] = dungeon_entrance
            key_layout.prize_relevant = prize_relevant_flag
            prize_lock_possible = True
        else:
            state.visit_region(region, key_checks=True)
            state.add_all_doors_check_keys(region, flat_proposal, world, player)
    if not prize_lock_possible:
        return  # done, no prize entrances to worry about
    expand_key_state(state, flat_proposal, world, player)
    while len(state.small_doors) > 0 or len(state.big_doors) > 0:
        if len(state.big_doors) > 0:
            open_a_door(state.big_doors[0].door, state, flat_proposal, world, player)
        elif len(state.small_doors) > 0:
            open_a_door(state.small_doors[0].door, state, flat_proposal, world, player)
        expand_key_state(state, flat_proposal, world, player)
    if any(x for x in state.found_locations if '- Prize' in x.name):
        key_layout.prize_can_lock = True


def cnt_avail_small_locations(free_locations, key_only, state, key_layout, world, player):
    std_flag = world.mode[player] == 'standard' and key_layout.sector.name == 'Hyrule Castle'
    if world.keyshuffle[player] == 'none' or std_flag:
        bk_adj = 1 if state.big_key_opened and not state.big_key_special else 0
        # this is the secret passage, could expand to Uncle/Links House with appropriate logic
        std_adj = 1 if std_flag and world.keyshuffle[player] != 'none' else 0
        avail_chest_keys = min(free_locations + std_adj - bk_adj, state.key_locations - key_only)
        return max(0, avail_chest_keys + key_only - state.used_smalls)
    return state.key_locations - state.used_smalls


def cnt_avail_small_locations_by_ctr(free_locations, counter, layout, world, player):
    std_flag = world.mode[player] == 'standard' and layout.sector.name == 'Hyrule Castle'
    if world.keyshuffle[player] == 'none' or std_flag:
        bk_adj = 1 if counter.big_key_opened and not layout.big_key_special else 0
        # this is the secret passage, could expand to Uncle/Links House with appropriate logic
        std_adj = 1 if std_flag and world.keyshuffle[player] != 'none' else 0
        avail_chest_keys = min(free_locations + std_adj - bk_adj, layout.max_chests)
        return max(0, avail_chest_keys + len(counter.key_only_locations) - counter.used_keys)
    return layout.max_chests + len(counter.key_only_locations) - counter.used_keys


def cnt_avail_big_locations(ttl_locations, state, world, player):
    if not world.bigkeyshuffle[player]:
        return max(0, ttl_locations - state.used_locations) if not state.big_key_special else 0
    return 1 if not state.big_key_special else 0


def cnt_avail_big_locations_by_ctr(ttl_locations, counter, layout, world, player):
    if not world.bigkeyshuffle[player]:
        bk_adj = 1 if counter.big_key_opened and not layout.big_key_special else 0
        used_locations = max(0, counter.used_keys - len(counter.key_only_locations)) + bk_adj
        return max(0, ttl_locations - used_locations) if not layout.big_key_special else 0
    return 1 if not layout.big_key_special else 0


def create_key_counters(key_layout, world, player):
    key_counters = {}
    key_layout.found_doors.clear()
    flat_proposal = key_layout.flat_prop
    state = ExplorationState(dungeon=key_layout.sector.name)
    state.init_zelda_event_doors(key_layout.event_starts, player)
    if world.doorShuffle[player] == 'vanilla':
        builder = world.dungeon_layouts[player][key_layout.sector.name]
        state.key_locations = len(builder.key_door_proposal) - builder.key_drop_cnt
    else:
        builder = world.dungeon_layouts[player][key_layout.sector.name]
        state.key_locations = max(0, builder.total_keys - builder.key_drop_cnt)
    state.big_key_special = False
    for region in key_layout.sector.regions:
        for location in region.locations:
            if location.forced_big_key():
                state.big_key_special = True
    for region in key_layout.start_regions:
        dungeon_entrance, portal_door = find_outside_connection(region)
        prize_relevant_flag = prize_relevance(key_layout, dungeon_entrance, world.is_atgt_swapped(player))
        if prize_relevant_flag:
            state.append_door_to_list(portal_door, state.prize_doors)
            state.prize_door_set[portal_door] = dungeon_entrance
            key_layout.prize_relevant = prize_relevant_flag
        else:
            state.visit_region(region, key_checks=True)
            state.add_all_doors_check_keys(region, flat_proposal, world, player)
    expand_key_state(state, flat_proposal, world, player)
    code = state_id(state, key_layout.flat_prop)
    key_counters[code] = create_key_counter(state, key_layout, world, player)
    queue = deque([(key_counters[code], state)])
    while len(queue) > 0:
        next_key_counter, parent_state = queue.popleft()
        for door in next_key_counter.child_doors:
            key_layout.found_doors.add(door)
            if door.dest in flat_proposal and door.type != DoorType.SpiralStairs:
                key_layout.found_doors.add(door.dest)
            child_state = parent_state.copy()
            if door.bigKey or door.name in get_special_big_key_doors(world, player):
                key_layout.key_logic.bk_doors.add(door)
            # open the door, if possible
            if can_open_door(door, child_state, key_layout, world, player):
                open_a_door(door, child_state, flat_proposal, world, player)
                expand_key_state(child_state, flat_proposal, world, player)
                code = state_id(child_state, key_layout.flat_prop)
                if code not in key_counters.keys():
                    child_kr = create_key_counter(child_state, key_layout, world, player)
                    key_counters[code] = child_kr
                    queue.append((child_kr, child_state))
    return key_counters


def find_outside_connection(region):
    portal = next((x for x in region.entrances if ' Portal' in x.parent_region.name), None)
    if portal:
        dungeon_entrance = next(x for x in portal.parent_region.entrances
                                if x.parent_region.type in [RegionType.LightWorld, RegionType.DarkWorld])
        portal_entrance = next(x for x in portal.parent_region.entrances if x.parent_region == region)
        return dungeon_entrance, portal_entrance.door
    return None, None


def can_open_door(door, state, key_layout, world, player):
    if state.big_key_opened:
        ttl_locations = count_free_locations(state, world, player)
    else:
        ttl_locations = count_locations_exclude_big_chest(state.found_locations, world, player)
    if door.smallKey:
        ttl_small_key_only = count_small_key_only_locations(state)
        available_small_locations = cnt_avail_small_locations(ttl_locations, ttl_small_key_only, state,
                                                              key_layout, world, player)
        return available_small_locations > 0
    elif door.bigKey:
        available_big_locations = cnt_avail_big_locations(ttl_locations, state, world, player)
        found_forced_bk = state.found_forced_bk()
        return not state.big_key_opened and (available_big_locations > 0 or found_forced_bk)
    else:
        return True


def can_open_door_by_counter(door, counter: KeyCounter, layout, world, player):
    if counter.big_key_opened:
        ttl_locations = len(counter.free_locations)
    else:
        ttl_locations = len([x for x in counter.free_locations if '- Big Chest' not in x.name])

    if door.smallKey:
        # ttl_small_key_only = len(counter.key_only_locations)
        return cnt_avail_small_locations_by_ctr(ttl_locations, counter, layout, world, player) > 0
    elif door.bigKey:
        if counter.big_key_opened:
            return False
        if layout.big_key_special:
            return any(x for x in counter.other_locations.keys() if x.forced_item and x.forced_item.bigkey)
        else:
            available_big_locations = cnt_avail_big_locations_by_ctr(ttl_locations, counter, layout, world, player)
            return available_big_locations > 0
    else:
        return True


def create_key_counter(state, key_layout, world, player):
    key_counter = KeyCounter(key_layout.max_chests)
    key_counter.child_doors.update(dict.fromkeys(unique_doors(state.small_doors+state.big_doors+state.prize_doors)))
    for loc in state.found_locations:
        if important_location(loc, world, player):
            key_counter.important_location = True
            key_counter.other_locations[loc] = None
            key_counter.important_locations[loc] = None
        elif loc.forced_item and loc.item.name == key_layout.key_logic.small_key_name:
            key_counter.key_only_locations[loc] = None
        elif loc.forced_item and loc.item.name == key_layout.key_logic.bk_name:
            key_counter.other_locations[loc] = None
        elif loc.name not in dungeon_events:
            key_counter.free_locations[loc] = None
        else:
            key_counter.other_locations[loc] = None
    key_counter.open_doors.update(dict.fromkeys(state.opened_doors))
    key_counter.used_keys = count_unique_sm_doors(state.opened_doors)
    key_counter.big_key_opened = state.big_key_opened
    if len(state.prize_door_set) > 0 and state.prize_doors_opened:
        key_counter.prize_doors_opened = True
    if any(x for x in key_counter.important_locations if '- Prize' in x.name):
        key_counter.prize_received = True
    return key_counter


imp_locations = None


def imp_locations_factory(world, player):
    global imp_locations
    if imp_locations:
        return imp_locations
    imp_locations = ['Agahnim 1', 'Agahnim 2', 'Attic Cracked Floor', 'Suspicious Maiden']
    if world.mode[player] == 'standard':
        imp_locations.append('Zelda Pickup')
        imp_locations.append('Zelda Drop Off')
    return imp_locations


def important_location(loc, world, player):
    return '- Prize' in loc.name or loc.name in imp_locations_factory(world, player) or (loc.forced_big_key())


def create_odd_key_counter(door, parent_counter, key_layout, world, player):
    odd_counter = KeyCounter(key_layout.max_chests)
    next_counter = find_next_counter(door, parent_counter, key_layout)
    odd_counter.free_locations = dict_difference(next_counter.free_locations, parent_counter.free_locations)
    odd_counter.key_only_locations = dict_difference(next_counter.key_only_locations, parent_counter.key_only_locations)
    odd_counter.child_doors = {}
    for d in next_counter.child_doors:
        if d not in parent_counter.child_doors and (d.type == DoorType.SpiralStairs or d.dest not in parent_counter.child_doors):
            odd_counter.child_doors[d] = None
    odd_counter.other_locations = dict_difference(next_counter.other_locations, parent_counter.other_locations)
    odd_counter.important_locations = dict_difference(next_counter.important_locations, parent_counter.important_locations)
    for loc in odd_counter.other_locations:
        if important_location(loc, world, player):
            odd_counter.important_location = True
    return odd_counter


def dict_difference(dict_a, dict_b):
    return dict.fromkeys([x for x in dict_a.keys() if x not in dict_b.keys()])


def dict_intersection(dict_a, dict_b):
    return dict.fromkeys([x for x in dict_a.keys() if x in dict_b.keys()])


def state_id(state, flat_proposal):
    s_id = '1' if state.big_key_opened else '0'
    for d in flat_proposal:
        s_id += '1' if d in state.opened_doors else '0'
    if len(state.prize_door_set) > 0:
        s_id += '1' if state.prize_doors_opened else '0'
    return s_id


def validate_id(state, flat_proposal):
    s_id = '1' if state.big_key_opened else '0'
    for d in flat_proposal:
        s_id += '1' if d in state.opened_doors else '0'
    if len(state.prize_door_set) > 0:
        s_id += '1' if state.prize_doors_opened else '0'
    s_id += str(state.used_locations)
    return s_id


def find_counter(opened_doors, bk_hint, key_layout, prize_flag, raise_on_error=True):
    counter = find_counter_hint(opened_doors, bk_hint, key_layout, prize_flag)
    if counter is not None:
        return counter
    more_doors = []
    for door in opened_doors.keys():
        more_doors.append(door)
        if door.dest not in opened_doors.keys():
            more_doors.append(door.dest)
    if len(more_doors) > len(opened_doors.keys()):
        counter = find_counter_hint(dict.fromkeys(more_doors), bk_hint, key_layout, prize_flag)
        if counter is not None:
            return counter
    if raise_on_error:
        cid = counter_id(opened_doors, bk_hint, key_layout.flat_prop, key_layout.prize_relevant, prize_flag)
        raise Exception(f'Unable to find door permutation. Init CID: {cid}')
    return None


def find_counter_hint(opened_doors, bk_hint, key_layout, prize_flag):
    cid = counter_id(opened_doors, bk_hint, key_layout.flat_prop, key_layout.prize_relevant, prize_flag)
    if cid in key_layout.key_counters.keys():
        return key_layout.key_counters[cid]
    if not bk_hint:
        cid = counter_id(opened_doors, True, key_layout.flat_prop, key_layout.prize_relevant, prize_flag)
        if cid in key_layout.key_counters.keys():
            return key_layout.key_counters[cid]
    return None


def find_max_counter(key_layout):
    max_counter = find_counter_hint(dict.fromkeys(key_layout.found_doors), False, key_layout, True)
    if max_counter is None:
        raise Exception("Max Counter is none - something is amiss")
    if len(max_counter.child_doors) > 0:
        max_counter = find_counter_hint(dict.fromkeys(key_layout.found_doors), True, key_layout, True)
    return max_counter


def counter_id(opened_doors, bk_unlocked, flat_proposal, prize_relevant, prize_flag):
    s_id = '1' if bk_unlocked else '0'
    for d in flat_proposal:
        s_id += '1' if d in opened_doors.keys() else '0'
    if prize_relevant:
        s_id += '1' if prize_flag else '0'
    return s_id


def cid(counter, key_layout):
    return counter_id(counter.open_doors, counter.big_key_opened, key_layout.flat_prop,
                      key_layout.prize_relevant, counter.prize_doors_opened)


# class SoftLockException(Exception):
#     pass


# vanilla validation code
def validate_vanilla_key_logic(world, player):
    validators = {
        'Hyrule Castle': val_hyrule,
        'Eastern Palace': val_eastern,
        'Desert Palace': val_desert,
        'Tower of Hera': val_hera,
        'Agahnims Tower': val_tower,
        'Palace of Darkness': val_pod,
        'Swamp Palace': val_swamp,
        'Skull Woods': val_skull,
        'Thieves Town': val_thieves,
        'Ice Palace': val_ice,
        'Misery Mire': val_mire,
        'Turtle Rock': val_turtle,
        'Ganons Tower': val_ganons
    }
    key_logic_dict = world.key_logic[player]
    for key, key_logic in key_logic_dict.items():
        validators[key](key_logic, world, player)


def val_hyrule(key_logic, world, player):
    if world.mode[player] == 'standard':
        val_rule(key_logic.door_rules['Hyrule Dungeon Map Room Key Door S'], 1)
        val_rule(key_logic.door_rules['Hyrule Dungeon Armory Interior Key Door N'], 2)
        val_rule(key_logic.door_rules['Sewers Dark Cross Key Door N'], 3)
        val_rule(key_logic.door_rules['Sewers Key Rat NE'], 4)
    else:
        val_rule(key_logic.door_rules['Sewers Secret Room Key Door S'], 2)
        val_rule(key_logic.door_rules['Sewers Dark Cross Key Door N'], 2)
        val_rule(key_logic.door_rules['Hyrule Dungeon Map Room Key Door S'], 2)
        val_rule(key_logic.door_rules['Hyrule Dungeon Armory Interior Key Door N'], 4)


def val_eastern(key_logic, world, player):
    val_rule(key_logic.door_rules['Eastern Dark Square Key Door WN'], 2, True, 'Eastern Palace - Big Key Chest', 1, {'Eastern Palace - Big Key Chest'})
    val_rule(key_logic.door_rules['Eastern Darkness Up Stairs'], 2)
    assert world.get_location('Eastern Palace - Big Chest', player) in key_logic.bk_restricted
    assert world.get_location('Eastern Palace - Boss', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 2


def val_desert(key_logic, world, player):
    val_rule(key_logic.door_rules['Desert East Wing Key Door EN'], 4)
    val_rule(key_logic.door_rules['Desert Tiles 1 Up Stairs'], 2)
    val_rule(key_logic.door_rules['Desert Beamos Hall NE'], 3)
    val_rule(key_logic.door_rules['Desert Tiles 2 NE'], 4)
    assert world.get_location('Desert Palace - Big Chest', player) in key_logic.bk_restricted
    assert world.get_location('Desert Palace - Boss', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 2


def val_hera(key_logic, world, player):
    val_rule(key_logic.door_rules['Hera Lobby Key Stairs'], 1, True, 'Tower of Hera - Big Key Chest')
    assert world.get_location('Tower of Hera - Big Chest', player) in key_logic.bk_restricted
    assert world.get_location('Tower of Hera - Compass Chest', player) in key_logic.bk_restricted
    assert world.get_location('Tower of Hera - Boss', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 3


def val_tower(key_logic, world, player):
    val_rule(key_logic.door_rules['Tower Room 03 Up Stairs'], 1)
    val_rule(key_logic.door_rules['Tower Dark Maze ES'], 2)
    val_rule(key_logic.door_rules['Tower Dark Archers Up Stairs'], 3)
    val_rule(key_logic.door_rules['Tower Circle of Pots ES'], 4)


def val_pod(key_logic, world, player):
    val_rule(key_logic.door_rules['PoD Arena Main NW'], 4)
    val_rule(key_logic.door_rules['PoD Basement Ledge Up Stairs'], 6, True, 'Palace of Darkness - Big Key Chest')
    val_rule(key_logic.door_rules['PoD Compass Room SE'], 6, True, 'Palace of Darkness - Harmless Hellway')
    val_rule(key_logic.door_rules['PoD Falling Bridge WN'], 6)
    val_rule(key_logic.door_rules['PoD Dark Pegs WN'], 6)
    assert world.get_location('Palace of Darkness - Big Chest', player) in key_logic.bk_restricted
    assert world.get_location('Palace of Darkness - Boss', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 2


def val_swamp(key_logic, world, player):
    val_rule(key_logic.door_rules['Swamp Entrance Down Stairs'], 1)
    val_rule(key_logic.door_rules['Swamp Pot Row WS'], 2)
    val_rule(key_logic.door_rules['Swamp Trench 1 Key Ledge NW'], 3)
    val_rule(key_logic.door_rules['Swamp Hub North Ledge N'], 5)
    val_rule(key_logic.door_rules['Swamp Hub WN'], 6)
    val_rule(key_logic.door_rules['Swamp Waterway NW'], 6)
    assert world.get_location('Swamp Palace - Entrance', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 1


def val_skull(key_logic, world, player):
    val_rule(key_logic.door_rules['Skull 3 Lobby NW'], 4)
    val_rule(key_logic.door_rules['Skull Spike Corner ES'], 5)


def val_thieves(key_logic, world, player):
    val_rule(key_logic.door_rules['Thieves Hallway WS'], 1)
    val_rule(key_logic.door_rules['Thieves Spike Switch Up Stairs'], 3)
    val_rule(key_logic.door_rules['Thieves Conveyor Bridge WS'], 3, True, 'Thieves\' Town - Big Chest')
    assert world.get_location('Thieves\' Town - Attic', player) in key_logic.bk_restricted
    assert world.get_location('Thieves\' Town - Boss', player) in key_logic.bk_restricted
    assert world.get_location('Thieves\' Town - Blind\'s Cell', player) in key_logic.bk_restricted
    assert world.get_location('Thieves\' Town - Big Chest', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 4


def val_ice(key_logic, world, player):
    val_rule(key_logic.door_rules['Ice Jelly Key Down Stairs'], 1)
    val_rule(key_logic.door_rules['Ice Conveyor SW'], 2)
    val_rule(key_logic.door_rules['Ice Backwards Room Down Stairs'], 5)
    assert world.get_location('Ice Palace - Boss', player) in key_logic.bk_restricted
    assert world.get_location('Ice Palace - Big Chest', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 2


def val_mire(key_logic, world, player):
    mire_west_wing = {'Misery Mire - Big Key Chest', 'Misery Mire - Compass Chest'}
    val_rule(key_logic.door_rules['Mire Spikes NW'], 3)  # todo: is sometimes 3 or 5? best_counter order matters
    # val_rule(key_logic.door_rules['Mire Spike Barrier NE'], 4)  # kind of a waste mostly
    val_rule(key_logic.door_rules['Mire Hub WS'], 5, False, None, 3, mire_west_wing)
    val_rule(key_logic.door_rules['Mire Conveyor Crystal WS'], 6, False, None, 4, mire_west_wing)
    assert world.get_location('Misery Mire - Boss', player) in key_logic.bk_restricted
    assert world.get_location('Misery Mire - Big Chest', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 2


def val_turtle(key_logic, world, player):
    # todo: check vanilla key logic when TR back doors are accessible
    if world.shuffle[player] == 'vanilla' and (not world.is_tile_swapped(0x05, player)) and world.logic[player] in ('noglitches', 'minorglitches'):
        val_rule(key_logic.door_rules['TR Hub NW'], 1)
        val_rule(key_logic.door_rules['TR Pokey 1 NW'], 2)
        val_rule(key_logic.door_rules['TR Chain Chomps Down Stairs'], 3)
        val_rule(key_logic.door_rules['TR Pokey 2 ES'], 6, True, 'Turtle Rock - Big Key Chest', 4, {'Turtle Rock - Big Key Chest'})
        val_rule(key_logic.door_rules['TR Crystaroller Down Stairs'], 5)
        val_rule(key_logic.door_rules['TR Dash Bridge WS'], 6)
        assert world.get_location('Turtle Rock - Eye Bridge - Bottom Right', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Eye Bridge - Top Left', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Eye Bridge - Top Right', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Eye Bridge - Bottom Left', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Boss', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Crystaroller Room', player) in key_logic.bk_restricted
        assert world.get_location('Turtle Rock - Big Chest', player) in key_logic.bk_restricted
        assert len(key_logic.bk_restricted) == 7


def val_ganons(key_logic, world, player):
    rando_room = {'Ganons Tower - Randomizer Room - Top Left', 'Ganons Tower - Randomizer Room - Top Right', 'Ganons Tower - Randomizer Room - Bottom Left', 'Ganons Tower - Randomizer Room - Bottom Right'}
    compass_room = {'Ganons Tower - Compass Room - Top Left', 'Ganons Tower - Compass Room - Top Right', 'Ganons Tower - Compass Room - Bottom Left', 'Ganons Tower - Compass Room - Bottom Right'}
    gt_middle = {'Ganons Tower - Big Key Room - Left', 'Ganons Tower - Big Key Chest', 'Ganons Tower - Big Key Room - Right', 'Ganons Tower - Bob\'s Chest', 'Ganons Tower - Big Chest'}
    val_rule(key_logic.door_rules['GT Double Switch EN'], 6, False, None, 4, rando_room.union({'Ganons Tower - Firesnake Room'}))
    val_rule(key_logic.door_rules['GT Hookshot ES'], 7, False, 'Ganons Tower - Map Chest', 5, {'Ganons Tower - Map Chest'})
    val_rule(key_logic.door_rules['GT Tile Room EN'], 6, False, None, 5, compass_room)
    val_rule(key_logic.door_rules['GT Firesnake Room SW'], 7, False, None, 5, rando_room)
    val_rule(key_logic.door_rules['GT Conveyor Star Pits EN'], 6, False, None, 5, gt_middle)  # should be 7?
    val_rule(key_logic.door_rules['GT Mini Helmasaur Room WN'], 6)  # not sure about this 6...
    val_rule(key_logic.door_rules['GT Crystal Circles SW'], 8)
    assert world.get_location('Ganons Tower - Mini Helmasaur Room - Left', player) in key_logic.bk_restricted
    assert world.get_location('Ganons Tower - Mini Helmasaur Room - Right', player) in key_logic.bk_restricted
    assert world.get_location('Ganons Tower - Big Chest', player) in key_logic.bk_restricted
    assert world.get_location('Ganons Tower - Pre-Moldorm Chest', player) in key_logic.bk_restricted
    assert world.get_location('Ganons Tower - Validation Chest', player) in key_logic.bk_restricted
    assert len(key_logic.bk_restricted) == 5


def val_rule(rule, skn, allow=False, loc=None, askn=None, setCheck=None):
    if setCheck is None:
        setCheck = set()
    assert rule.small_key_num == skn
    assert rule.allow_small == allow
    assert rule.small_location == loc or rule.small_location.name == loc
    assert rule.alternate_small_key == askn
    assert len(setCheck) == len(rule.alternate_big_key_loc)
    for loc in rule.alternate_big_key_loc:
        assert loc.name in setCheck


# Soft lock stuff
def validate_key_placement(key_layout, world, player):
    if world.keyshuffle[player] == 'universal' or world.accessibility[player] == 'none':
        return True  # Can't keylock in retro.  Expected if beatable only.
    max_counter = find_max_counter(key_layout)
    keys_outside = 0
    big_key_outside = False
    smallkey_name = dungeon_keys[key_layout.sector.name]
    bigkey_name = dungeon_bigs[key_layout.sector.name]
    if world.keyshuffle[player] != 'none':
        keys_outside = key_layout.max_chests - sum(1 for i in max_counter.free_locations if i.item is not None and i.item.name == smallkey_name and i.item.player == player)
    if world.bigkeyshuffle[player]:
        max_counter = find_max_counter(key_layout)
        big_key_outside = bigkey_name not in (l.item.name for l in max_counter.free_locations if l.item)
    for i in world.precollected_items:
        if i.player == player and i.name == bigkey_name:
            big_key_outside = True
            break
        if i.player == player and i.name == smallkey_name:
            keys_outside += 1

    if world.logic[player] == 'hybridglitches':
        # Swamp keylogic
        if smallkey_name.endswith('(Swamp Palace)'):
            swamp_entrance = world.get_location('Swamp Palace - Entrance', player)
            # Swamp small not vanilla
            if swamp_entrance.item is None or (swamp_entrance.item.name != smallkey_name or swamp_entrance.item.player != player):
                mire_keylayout = world.key_layout[player]['Misery Mire']
                mire_smallkey_name = dungeon_keys[mire_keylayout.sector.name]
                # Check if any mire keys are in swamp (excluding entrance), if none then add one to keys_outside
                mire_keys_in_swamp = sum([1 if x.item.name == mire_smallkey_name else 0 for x in key_layout.item_locations if x.item is not None and x != swamp_entrance])
                if mire_keys_in_swamp == 0:
                    keys_outside +=1 
        # Mire keylogic
        if smallkey_name.endswith('(Tower of Hera)'):
            # TODO: Make sure that mire medallion isn't in hera basement, or if it is, the small key is available downstairs
            big_key_outside = True
    for code, counter in key_layout.key_counters.items():
        if len(counter.child_doors) == 0:
            continue
        if key_layout.big_key_special:
            big_found = any(i.forced_item is not None and i.item.bigkey for i in counter.other_locations) or big_key_outside
        else:
            big_found = any(i.item is not None and i.item.name == bigkey_name for i in counter.free_locations if "- Big Chest" not in i.name) or big_key_outside
        if counter.big_key_opened and not big_found:
            continue  # Can't get to this state
        found_locations = set(i for i in counter.free_locations if big_found or "- Big Chest" not in i.name)
        found_keys = sum(1 for i in found_locations if i.item is not None and i.item.name == smallkey_name and i.item.player == player) + \
                     len(counter.key_only_locations) + keys_outside
        if key_layout.prize_relevant:
            found_prize = any(x for x in counter.important_locations if '- Prize' in x.name)
            if not found_prize and dungeon_table[key_layout.sector.name].prize:
                prize_loc = world.get_location(dungeon_table[key_layout.sector.name].prize, player)
                if key_layout.prize_relevant == 'BigBomb':
                    found_prize = prize_loc.item.name not in ['Crystal 5', 'Crystal 6']
                elif key_layout.prize_relevant == 'GT':
                    found_prize = 'Crystal' not in prize_loc.item.name or world.crystals_needed_for_gt[player] < 7
        else:
            found_prize = False
        can_progress = (not counter.big_key_opened and big_found and any(d.bigKey for d in counter.child_doors)) or \
            found_keys > counter.used_keys and any(not d.bigKey for d in counter.child_doors) or \
            self_locked_child_door(key_layout, counter) or \
            (key_layout.prize_relevant and not counter.prize_doors_opened and found_prize)
        if not can_progress:
            missing_locations = set(max_counter.free_locations.keys()).difference(found_locations)
            missing_items = [l for l in missing_locations if l.item is None or (l.item.name != smallkey_name and l.item.name != bigkey_name) or "- Boss" in l.name]
            # missing_key_only = set(max_counter.key_only_locations.keys()).difference(counter.key_only_locations.keys()) # do freestanding keys matter for locations?
            if len(missing_items) > 0:  # world.accessibility[player]=='locations' and (len(missing_locations)>0 or len(missing_key_only) > 0):
                logging.getLogger('').error("Keylock - can't open locations: ")
                logging.getLogger('').error("code: " + code)
                for i in missing_locations:
                    logging.getLogger('').error(i)
                return False

    return True


def self_locked_child_door(key_layout, counter):
    if len(counter.child_doors) == 1:
        door = next(iter(counter.child_doors.keys()))
        return door.smallKey and key_layout.key_logic.door_rules[door.name].allow_small
    return False


