import numpy as np

from .default_data import body_connections, DEFAULT_RADIUS

def create_people_masks(data, rads, h, w, weigth):
    return split_masks(data['people'], h, w, weigth, create_people_mask(data, rads, h, w))

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

def create_people_mask(data, rads, h, w):
    distance_mask = np.full((h, w), np.inf)
    mask = np.zeros((h, w), dtype=np.int)
    for person_id, person in enumerate(data['people']):
        keypoints = np.array(person['pose_keypoints_2d']).reshape(-1, 3)
        radius = rads[person_id] if person_id < len(rads) else DEFAULT_RADIUS

        for x, y, c in keypoints:
            if c == 0:
                continue
            x, y = int(x), int(y)

            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    pre_norm = dx*dx + dy*dy
                    if pre_norm > radius*radius: continue

                    x_new, y_new = x + dx, y + dy

                    if not (0 <= x_new < w and 0 <= y_new < h): continue

                    dist = np.sqrt(pre_norm)

                    if dist < distance_mask[y_new, x_new]:
                        mask[y_new, x_new] = person_id + 1
                        distance_mask[y_new, x_new] = dist

        for i, j in body_connections:
            x1, y1, c1 = keypoints[i]
            x2, y2, c2 = keypoints[j]
            if c1 == 0 or c2 == 0:
                continue

            x_min = max(0, int(min(x1, x2) - radius))
            x_max = min(w, int(max(x1, x2) + radius))
            y_min = max(0, int(min(y1, y2) - radius))
            y_max = min(h, int(max(y1, y2) + radius))

            for x in range(x_min, x_max):
                for y in range(y_min, y_max):
                    dist = point_to_line_dist(x, y, x1, y1, x2, y2)

                    if dist < radius and dist < distance_mask[y, x]:
                        mask[y, x] = person_id + 1
                        distance_mask[y, x] = dist
    return mask

def point_to_line_dist(x, y, x1, y1, x2, y2):
    line_len_squared = (x2 - x1)**2 + (y2 - y1)**2
    if line_len_squared == 0:
        return np.sqrt((x - x1)**2 + (y - y1)**2)
    t = max(0, min(1, ((x - x1)*(x2 - x1) + (y - y1)*(y2 - y1)) / line_len_squared))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return np.sqrt((x - proj_x)**2 + (y - proj_y)**2)
