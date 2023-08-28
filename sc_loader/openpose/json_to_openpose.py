import re
import json
import base64

import cv2
import numpy as np

from .default_data import connect_color, connect_keypoints, def_rel_keypoints
from .mask import create_people_masks
from .. import context as c

ADD_DEFAULT = False
DEFAULT_RADIUS = 60

def from_json(json_path, payload):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    w, h = data['canvas_width'], data['canvas_height']
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    if 'people' in data:
        from_people(data['people'], canvas, w, h)
        rads = get_rads_from_context(payload)
        c.poses_masks_generated = create_people_masks(data, rads, h, w, weigth=1)
        for i, m in enumerate(c.poses_masks_generated):
            cv2.imwrite(f'pose_{i}.png', (m * 255).astype('uint8'))
    else:
        from_keypoints(data['people'], canvas)

    _, buffer = cv2.imencode('.jpg', canvas)
    return base64.b64encode(buffer).decode()

def from_people(people, canvas, w, h, lin_rad=3, circle_rad=4):
    people_chunks = [
        [
            keypoints['pose_keypoints_2d'][i:i+3]
            for i in range(0, len(keypoints['pose_keypoints_2d']), 3)
        ]
        for keypoints in people
    ]

    people_points = handle_default_points([
        [
            [-1, -1] if chunk[2] == 0 else [chunk[0] * chunk[2], chunk[1] * chunk[2]]
            for chunk in chunks
        ]
        for chunks in people_chunks
    ], w, h)

    for points in people_points:
        add_pose(canvas, points, lin_rad, circle_rad)

def from_keypoints(keypoints, canvas):
    points = [
        keypoints[i:i+18]
        for i in range(0, len(keypoints), 18)
    ]

    for point in points:
        add_pose(canvas, point, DEFAULT_RADIUS, DEFAULT_RADIUS)

def add_pose(canvas, keypoints, lin_rad, circle_rad):
    for i, ckp in enumerate(connect_keypoints):
        if not any(keypoints[point] == [-1, -1] for point in ckp):
            cv2.line(canvas, int_coord(keypoints[ckp[0]]), int_coord(keypoints[ckp[1]]), connect_color[i], lin_rad)

    for i, kp in enumerate(keypoints):
        if kp != [-1, -1]:
            cv2.circle(canvas, int_coord(kp), circle_rad, connect_color[i], -1)

def get_rads_from_context(payload):
    return [int(radius) for radius in re.findall(r'@(\d+)', payload['alwayson_scripts']['Sc Latent Couple']['args'][2].replace('_', f'@{DEFAULT_RADIUS}'))]

def handle_default_points(people_points, w, h):
    if ADD_DEFAULT:
        for points in people_points:
            while any(pos == [-1, -1] for pos in points):
                for i in range(len(points)):
                    if points[i][0] == -1:
                        continue
                    for j in range(len(points)):
                        if (points[j][0] == -1) and any(cp in ([i, j], [j, i]) for cp in connect_keypoints):
                            x = points[i][0] + def_rel_keypoints[i][j][0]
                            y = points[i][1] + def_rel_keypoints[i][j][1]
                            x = min(max(x, 0), w)
                            y = min(max(y, 0), h)
                            points[j] = [x, y]
    return people_points

def int_coord(coord):
    return (int(coord[0]), int(coord[1]))
