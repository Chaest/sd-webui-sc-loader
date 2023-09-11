import re
import base64

import yaml
import cv2
import numpy as np

from sonotoria import jaml

from .common import COLORS, CONNECTIONS, DEFAULT_RADIUS, HAND_CONNECTIONS, HAND_POINTS_COLOR
from .sc_mask import create_people_masks
from .person import load_people
from ..json_to_openpose import handle_faces, handle_hands
from ..default_data import hand_colors, hand_connections
from ... import context as c

def from_sc_pose(sc_pose_path, payload):
    with open(sc_pose_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    w, h = data['canvas']['width'], data['canvas']['height']
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    from_people(data['people'], canvas)
    rads = get_rads_from_context(payload)
    c.poses_masks_generated, mask, max_layer = create_people_masks(data, rads, weigth=1)
    layer_value = int(255 / (max_layer + 1))
    pose_depthmask = ((mask+1) * layer_value).astype('uint8')
    cv2.imwrite('sc_depthmap.png', pose_depthmask)
    for i, m in enumerate(c.poses_masks_generated):
        cv2.imwrite(f'sc_pose_{i}.png', (m * 255).astype('uint8'))

    _, buffer = cv2.imencode('.jpg', canvas)
    _, buffer_depth = cv2.imencode('.jpg', pose_depthmask)
    return base64.b64encode(buffer).decode(), base64.b64encode(buffer_depth).decode()

def from_people(people, canvas, lin_rad=3, circle_rad=4):
    for person in people:
        for part_name, part_data in person['parts'].items():
            cv2.circle(canvas, int_coord(part_data['coordinates']), circle_rad, COLORS[part_name], -1)

        for p1, p2 in CONNECTIONS:
            if p1 in person['parts'] and p2 in person['parts']:
                cv2.line(
                    canvas,
                    int_coord(person['parts'][p1]['coordinates']),
                    int_coord(person['parts'][p2]['coordinates']),
                    COLORS[p1],
                    lin_rad
                )
    draw_hands_and_face(people, canvas, lin_rad, circle_rad)

def draw_hands_and_face(people, canvas, lin_rad, circle_rad):
    for person in people:
        draw_hand(person.get('left_hand'), canvas, lin_rad*0.8, circle_rad*0.7)
        draw_hand(person.get('right_hand'), canvas, lin_rad*0.8, circle_rad*0.7)
        draw_face(person.get('face'), canvas, circle_rad*0.6)

def draw_hand(hand, canvas, lin_rad, circle_rad):
    if hand is None: return
    for _, part_data in hand.items():
        cv2.circle(canvas, int_coord(part_data['coordinates']), int(circle_rad), HAND_POINTS_COLOR, -1)

    for p1, p2, color in HAND_CONNECTIONS:
        if p1 in hand and p2 in hand:
            cv2.line(
                canvas,
                int_coord(hand[p1]['coordinates']),
                int_coord(hand[p2]['coordinates']),
                color,
                int(lin_rad)
            )

def draw_face(face, canvas, circle_rad):
    if face is None: return

    for point in face['points']:
        cv2.circle(canvas, int_coord(point), int(circle_rad), [255, 255, 255], -1)

def get_rads_from_context(payload):
    try:
        return [int(radius) for radius in re.findall(r'@(\d+)', payload['alwayson_scripts']['Sc Latent Couple']['args'][2].replace('_', f'@{DEFAULT_RADIUS}'))]
    except KeyError: # ControlNet without Sc Latent
        return []

def int_coord(coord):
    return (int(coord[0]), int(coord[1]))

def openpose_to_scpose(openpose):
    jaml.dump(
        'test.yaml',
        {
            'width': openpose['canvas_width'],
            'height': openpose['canvas_height'],
            'people': load_people(openpose)
        }
    )
