import base64
from datetime import datetime

import cv2

from . import context as c

DEFAULT_PAYLOAD_DATA = {
    'steps': 35,
    'cfg_scale': 7.5,
    'width': 512,
    'height': 512
}


def create_payload(current_dir):
    payload = DEFAULT_PAYLOAD_DATA | c.sc_data['base_payload'] | c.batch_data
    update_cn_data(payload, current_dir)
    update_hr_data(payload)
    update_rf_data(payload)
    update_or_data(payload)
    return payload | build_prompts()

def update_or_data(payload):
    if c.sampler:
        payload['sampler_name'] = c.database['samplers'][c.sampler]
    if c.steps:
        payload['steps'] = c.steps
    if c.cfg_scale:
        payload['cfg_scale'] = c.cfg_scale

def update_rf_data(payload):
    if c.restore:
        payload['restore_faces'] = True

def update_hr_data(payload):
    if c.hr:
        payload['enable_hr'] = True
        payload['denoising_strength'] = 0.37
        payload['hr_scale'] = 2.5
        payload['hr_upscaler'] = c.database['upscalers'][c.upscaler]
        payload['batch_size'] = 3
        w = payload['width']
        h = payload['height']
        if w > 512 or h > 512:
            mx = max(w, h)
            ratio = float(512)/float(mx)
            payload['width'] = int(float(payload['width']) * ratio)
            payload['height'] = int(float(payload['height']) * ratio)


def update_cn_data(payload, current_dir):
    if 'alwayson_scripts' not in payload or 'controlnet' not in payload['alwayson_scripts']:
        return
    cn_data = payload['alwayson_scripts']['controlnet']
    cn_units = cn_data['args']
    cn_data['args'] = [
        {
            'input_image': load_img_str(current_dir + '/poses/' + unit['input_image'] + '.png'),
            'model': c.database['cn_models'][unit['model']]
        }
        for unit in cn_units
    ]

def expand_prompt(prompt):
    expanders = [word for word in prompt.replace('\n', ' ').replace(',', ' ').split(' ') if word and word[0] == '$']
    for expander in expanders:
        prompt = prompt.replace(expander, c.database['prompts'][expander[1:]])
    return prompt

def build_prompts():
    build_short_prompt()
    chars = c.sc_data['characters']
    chars_prompts = '\nAND\n'.join([
        ','.join((
            c.sc_data['prompts'][char]['pre'],
            c.database['prompts']['characters'][c.chars[idx]],
            c.sc_data['prompts'][char]['post']
        ))
        for idx, char in enumerate(chars)
    ])
    positive_prompt = '\n'.join((
        c.sc_data['prompts']['quality'],
        c.sc_data['prompts']['general'],
        'AND',
        chars_prompts
    ))
    negative_prompt = c.sc_data['prompts']['negative']

    return {
        'prompt': expand_prompt(positive_prompt),
        'negative_prompt': expand_prompt(negative_prompt)
    }

def build_short_prompt():
    positive_prompt = '\n'.join((
        f'[[Scenario Loader v{c.version}]]',
        '## ' + datetime.today().strftime('%Y-%m-%d'),
        c.sc_data['prompts']['quality'],
        f'scenario: {c.scenario}',
        '\n'.join([f'@{c.chars[idx]}' for idx, _ in enumerate(c.sc_data['characters'])])
    ))
    negative_prompt = c.sc_data['prompts']['negative']

    c.short_prompts = {
        'positive': positive_prompt,
        'negative': negative_prompt
    }

def load_img_str(img_path):
    return base64.b64encode(cv2.imencode('.png', cv2.imread(img_path))[1]).decode('utf-8')