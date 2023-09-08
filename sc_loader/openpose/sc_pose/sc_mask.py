import numpy as np

from .common import DEFAULT_RADIUS

CONNECTIONS = (
    ( 'nose',           'neck'           ),
    ( 'nose',           'right_eye'      ),
    ( 'nose',           'left_eye'       ),
    ( 'right_eye',      'right_ear'      ),
    ( 'left_eye',       'left_ear'       ),
    ( 'neck',           'right_shoulder' ),
    ( 'neck',           'left_shoulder'  ),
    ( 'neck',           'right_hip'      ),
    ( 'neck',           'left_hip'       ),
    ( 'right_shoulder', 'right_elbow'    ),
    ( 'left_shoulder',  'left_elbow'     ),
    ( 'right_elbow',    'right_wrist'    ),
    ( 'left_elbow',     'left_wrist'     ),
    ( 'right_hip',      'right_knee'     ),
    ( 'left_hip',       'left_knee'      ),
    ( 'right_knee',     'right_ankle'    ),
    ( 'left_knee',      'left_ankle'     ),
)

def create_people_masks(data, rads, weigth):
    h, w = data['canvas']['height'], data['canvas']['width']
    mask, layer_mask, max_layer = create_people_mask(data, rads, h, w)
    return split_masks(data['people'], h, w, weigth, mask), layer_mask, max_layer

def create_people_mask(data, rads, h, w):
    distance_mask = np.full((h, w), np.inf)
    layer_mask = np.full((h, w), -1, dtype=int)
    mask = np.zeros((h, w), dtype=int)
    max_layer = 0

    for person_id, person in enumerate(data['people']):
        radius = rads[person_id] if person_id < len(rads) else DEFAULT_RADIUS
        person_parts = person['parts']

        nmax = update_masks_for_person_points(person_id, person_parts, radius, h, w, mask, distance_mask, layer_mask)
        update_masks_for_person_lines(person_id, person_parts, radius-15, h, w, mask, distance_mask, layer_mask)
        if nmax > max_layer:
            max_layer = nmax

    return mask, layer_mask, max_layer

def update_masks_for_person_points(person_id, person_parts, radius, h, w, mask, distance_mask, layer_mask):
    max_layer = 0
    for _, part_data in person_parts.items():
        coords = part_data['coordinates']
        x, y = int(coords[0]), int(coords[1])

        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                pre_norm = dx*dx + dy*dy
                if pre_norm > radius*radius: continue

                x_new, y_new = x + dx, y + dy

                if not (0 <= x_new < w and 0 <= y_new < h): continue
                if layer_mask[y_new, x_new] > part_data['layer']: continue

                dist = np.sqrt(pre_norm)


                if part_data['layer'] > max_layer:
                    max_layer = part_data['layer']
                if layer_mask[y_new, x_new] < part_data['layer'] or dist < distance_mask[y_new, x_new]:
                    mask[y_new, x_new] = person_id + 1
                    distance_mask[y_new, x_new] = dist
                    layer_mask[y_new, x_new] = part_data['layer']

    return max_layer

def update_masks_for_person_lines(person_id, person_parts, radius, h, w, mask, distance_mask, layer_mask):
    for p1, p2 in CONNECTIONS:
        if p1 not in person_parts or p2 not in person_parts:
            continue
        x1, y1 = person_parts[p1]['coordinates']
        x2, y2 = person_parts[p2]['coordinates']

        x_min = max(0, int(min(x1, x2) - radius))
        x_max = min(w, int(max(x1, x2) + radius))
        y_min = max(0, int(min(y1, y2) - radius))
        y_max = min(h, int(max(y1, y2) + radius))

        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                dist = point_to_line_dist(x, y, x1, y1, x2, y2)

                if person_parts[p1]['layer'] != person_parts[p2]['layer']:
                    dt1 = np.sqrt((x - x1)**2 + (y - y1)**2)
                    dt2 = np.sqrt((x - x2)**2 + (y - y2)**2)
                    layer = person_parts[p1]['layer'] if dt1 < dt2 else person_parts[p2]['layer']
                else:
                    layer = person_parts[p1]['layer']

                if layer_mask[y, x] > layer: continue
                if dist < radius and (layer_mask[y, x] < layer or dist < distance_mask[y, x]):
                    mask[y, x] = person_id + 1
                    distance_mask[y, x] = dist
                    layer_mask[y, x] = layer


def split_masks(people, h, w, weigth, mask):
    masks = [
        np.full((h, w), 0)
        for _ in range(len(people))
    ]
    for x in range(len(mask)):
        for y in range(len(mask[x])):
            if mask[x][y] > 0:
                masks[mask[x][y] - 1][x][y] = weigth
    return masks

def point_to_line_dist(x, y, x1, y1, x2, y2):
    line_len_squared = (x2 - x1)**2 + (y2 - y1)**2
    if line_len_squared == 0:
        return np.sqrt((x - x1)**2 + (y - y1)**2)
    t = max(0, min(1, ((x - x1)*(x2 - x1) + (y - y1)*(y2 - y1)) / line_len_squared))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return np.sqrt((x - proj_x)**2 + (y - proj_y)**2)