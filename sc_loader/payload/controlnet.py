import base64
import random

import cv2

from modules.shared import opts

from .. import context as c

OPENPOSE_MODEL = 'control_sd15_openpose [fef5e48e]'

def load_img_str(img_path):
    return base64.b64encode(cv2.imencode('.png', cv2.imread(img_path))[1]).decode('utf-8') # pylint: disable=no-member

def get_pose(unit):
    img = unit['input_image']
    if c.database['series'].get('poses', {}).get(img):
        return random.choice(c.database['series']['poses'][img])
    return img

def pose_to_img(pose):
    if '.' not in pose:
        pose += '.png'
    return load_img_str(f'{opts.sc_loader_config_path}/poses/{pose}')

def update_cn_data(payload):
    if 'alwayson_scripts' not in payload or 'controlnet' not in payload['alwayson_scripts']:
        return
    cn_data = payload['alwayson_scripts']['controlnet']
    cn_units = cn_data['args']
    cn_data['args'] = [
        {
            'model': OPENPOSE_MODEL,
            **unit,
            'input_image': pose_to_img(get_pose(unit))
        }
        for unit in cn_units
    ]
