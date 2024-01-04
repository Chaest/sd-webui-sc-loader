import io
import base64
import random
from PIL import Image

import cv2

from .. import context as c
from ..openpose.json_to_openpose import from_json
from ..openpose.sc_pose.convert import from_sc_pose

OPENPOSE_MODEL = 'control_sd15_openpose [fef5e48e]'
OPENPOSE_MODEL_DEPTH = 'control_sd15_depth [fef5e48e]'

def load_img_str(img_path):
    return base64.b64encode(cv2.imencode('.png', cv2.imread(img_path))[1]).decode('utf-8') # pylint: disable=no-member

def get_pose(unit):
    img = unit['input_image']
    if c.database['series'].get('poses', {}).get(img):
        return random.choice(c.database['series']['poses'][img])
    return img

def pose_to_img(pose, payload):
    if pose.endswith('.json'):
        return from_json(f'{c.get_cfg_path()}/poses/{pose}', payload)
    if pose.endswith('.yaml') or pose.endswith('.yml'):
        pose, _ = from_sc_pose(f'{c.get_cfg_path()}/poses/{pose}', payload)
        return pose
    if '.' not in pose:
        pose += '.png'
    return load_img_str(f'{c.get_cfg_path()}/poses/{pose}')

def update_cn_data(payload):
    if 'alwayson_scripts' not in payload or 'controlnet' not in payload['alwayson_scripts']:
        return
    cn_data = payload['alwayson_scripts']['controlnet']
    cn_units = cn_data['args']
    if 'model' not in cn_units[0] or cn_units[0]['model'] in (OPENPOSE_MODEL, OPENPOSE_MODEL_DEPTH):
        width, height = Image.open(io.BytesIO(base64.b64decode(pose_to_img(get_pose(cn_units[0]), payload)))).size
        payload['height'] = height
        payload['width'] = width
    for unit in cn_data['args']:
        if 'model' not in unit:
            unit['model'] = OPENPOSE_MODEL
        if 'input_image' in unit:
            unit['input_image'] = pose_to_img(get_pose(unit), payload)
