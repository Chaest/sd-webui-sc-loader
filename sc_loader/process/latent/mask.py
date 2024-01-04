import numpy as np
from PIL import Image

COLORS = [
    (0, 0, 0),       # Black
    (255, 255, 255), # White
    (255, 0, 0),     # Red
    (0, 255, 0),     # Lime Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (0, 255, 255),   # Cyan (Aqua)
    (255, 0, 255),   # Magenta (Fuchsia)
    (192, 192, 192), # Silver (Light Gray)
    (255, 165, 0),   # Orange
]


def masks_from_colors(image):
    image_np = np.array(image.convert('RGB'))
    masks = [np.ones(image_np.shape[:2], dtype=np.uint8)]

    non_matching_mask = np.ones(image_np.shape[:2], dtype=np.uint8)

    for color in COLORS:
        color_mask = np.all(image_np == color, axis=-1).astype(np.uint8)
        if np.any(color_mask):
            masks.append(color_mask)
            non_matching_mask = np.bitwise_and(non_matching_mask, np.bitwise_not(color_mask))

    masks.append(non_matching_mask)

    return masks
