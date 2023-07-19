import base64
import random
import copy
from datetime import datetime

import cv2

from modules.shared import opts

from . import context as c

DEFAULT_PAYLOAD_DATA = {
    'steps': 35,
    'cfg_scale': 7.5,
    'width': 512,
    'height': 512,
    'seed_resize_from_h': 0,
    'seed_resize_from_w': 0,
    'restore_faces': False,
    'sampler_name': 'DPM++ 2M Karras',
    'seed': -1,
    'override_settings_restore_afterwards': True
}


def create_payloads(model, scenario, *characters):
    payload = DEFAULT_PAYLOAD_DATA | scenario['base_payload']
    payload = copy.deepcopy(payload)
    update_cn_data(payload)
    update_hr_data(payload)
    update_data(payload, model)
    for _ in range(c.nb_repeats):
        yield payload | build_prompts(scenario, characters)

def update_data(payload, model):
    payload['override_settings'] = {'sd_model_checkpoint': model}
    payload['batch_size'] = c.nb_iter
    payload['n_iter'] = c.nb_batches
    if c.sampler:
        payload['sampler_name'] = c.sampler
    if c.steps:
        payload['steps'] = c.steps
    if c.cfg_scale:
        payload['cfg_scale'] = c.cfg_scale
    if c.restore:
        payload['restore_faces'] = True

def update_hr_data(payload):
    if c.hr:
        payload['enable_hr'] = True
        payload['denoising_strength'] = 0.37
        payload['hr_scale'] = 2.5
        payload['hr_upscaler'] = c.upscaler or 'R-ESRGAN 4x+'
        payload['batch_size'] = 3
        w = payload['width']
        h = payload['height']
        if w > 512 or h > 512:
            mx = max(w, h)
            ratio = float(512)/float(mx)
            payload['width'] = int(float(payload['width']) * ratio)
            payload['height'] = int(float(payload['height']) * ratio)

def update_cn_data(payload):
    if 'alwayson_scripts' not in payload or 'controlnet' not in payload['alwayson_scripts']:
        return
    cn_data = payload['alwayson_scripts']['controlnet']
    cn_units = cn_data['args']
    cn_data['args'] = [
        {
            'input_image': load_img_str(opts.sc_loader_config_path + '/poses/' + unit['input_image'] + '.png'),
            'model': 'control_sd15_openpose [fef5e48e]'
        }
        for unit in cn_units
    ]

def expand_prompt(prompt):
    expanders = [word for word in prompt.replace('\n', ' ').replace(',', ' ').split(' ') if word and word[0] == '$']
    for expander in expanders:
        expander_value = c.database['prompts'][expander[1:]]
        expanded_value = expander_value if isinstance(expander_value, str) else random.choice(expander_value)
        prompt = prompt.replace(expander, expanded_value)
    return prompt

def build_prompts(scenario, characters):
    build_short_prompt(scenario)
    chars_prompts = []
    chars_neg_prompts = []
    for i in range(len(scenario['characters'])):
        character_type = scenario['characters'][i]
        sc_char_prompt = scenario['prompts'][character_type]
        db_char_prompt = c.database['prompts']['characters'][characters[i]]
        if isinstance(db_char_prompt, list):
            chars_neg_prompts.append(db_char_prompt[1])
            db_char_prompt = db_char_prompt[0]
        chars_prompts.append(','.join((sc_char_prompt['pre'], db_char_prompt, sc_char_prompt['post'])))

    positive_prompt = '\n'.join((
        scenario['prompts']['quality'],
        scenario['prompts']['general']
    ))
    positive_prompt = ' AND '.join([positive_prompt, *chars_prompts])
    negative_prompt = scenario['prompts']['negative'] + ',' + ','.join(chars_neg_prompts)

    return {
        'prompt': expand_prompt(positive_prompt),
        'negative_prompt': expand_prompt(negative_prompt)
    }

def build_short_prompt(scenario):
    positive_prompt = '\n'.join((
        f'[[Scenario Loader v{c.version}]]',
        '## ' + datetime.today().strftime('%Y-%m-%d'),
        scenario['prompts']['quality'],
        f'scenario: {c.scenario}',
        '\n'.join([f'@{c.chars[idx]}' for idx, _ in enumerate(scenario['characters'])])
    ))
    negative_prompt = scenario['prompts']['negative']

    c.short_prompts = {
        'positive': positive_prompt,
        'negative': negative_prompt
    }

def load_img_str(img_path):
    return base64.b64encode(cv2.imencode('.png', cv2.imread(img_path))[1]).decode('utf-8')