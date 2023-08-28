import re
from dataclasses import dataclass

from .filters import create_filter

DIVISIONS_RGXP = r'(?:\s*,\s*)?((?:\d+:\d+)|(?:\((?:\d+:\d+(?:\s*,\s*)?)+\))|(?:@\d+))'
POSITIONS_RGXP = r'(?:\s*,\s*)?((?:\d+(?:-\d+)?:\d+(?:-\d+)?)|(?:\((?:\d+(?:-\d+)?:\d+(?:-\d+)?(?:\s*,\s*)?)+\))|(?:_)|(?:@\d+))'

@dataclass
class Division:
    y: float
    x: float

@dataclass
class Position:
    y: float
    x: float
    ey: float
    ex: float

def params_to_filters(raw_divisions, raw_positions, raw_weights, pose_masks):
    division_groups = extract_division_groups(raw_divisions)
    position_groups = extract_positions_groups(raw_positions)
    weights = [float(weight) for weight in raw_weights.split(',')]

    return [
        create_filter(divisions, positions, weight, pose_masks)
        for divisions, positions, weight in zip(division_groups, position_groups, weights)
    ]

def extract_division_groups(divisions):
    division_groups = []
    for division_group_raw in re.findall(DIVISIONS_RGXP, divisions):
        if division_group_raw[0] == '(' and division_group_raw[-1] == ')':
            group = [
                divisions.strip().split(':')
                for divisions in division_group_raw[1:-1].split(',')
            ]
        elif division_group_raw[0] == '@':
            group = int(division_group_raw[1:])
            division_groups.append(group)
            continue
        else:
            group = [division_group_raw.split(':')]
        group = [Division(float(division[0]), float(division[1])) for division in group]
        division_groups.append(group)
    return division_groups

def extract_positions_groups(positions):
    position_groups = []
    for position_group_raw in re.findall(POSITIONS_RGXP, positions):
        if position_group_raw[0] == '(' and position_group_raw[-1] == ')':
            group = [
                positions.strip().split(':')
                for positions in position_group_raw[1:-1].split(',')
            ]
        elif position_group_raw[0] in ('_', '@'):
            group = position_group_raw[1:]
            position_groups.append(group)
            continue
        else:
            group = [position_group_raw.split(':')]
        for i, position in enumerate(group):
            y, x = position
            y1, y2 = start_and_end_position(y)
            x1, x2 = start_and_end_position(x)
            group[i] = Position(y1, x1, y2, x2)
        position_groups.append(group)
    return position_groups

def start_and_end_position(raw):
    nums = [float(num) for num in raw.split('-')]
    return (nums[0], nums[0] + 1.0) if len(nums) == 1 else nums
