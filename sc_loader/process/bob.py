'''
    The name "bob" stands for "batch of batches" which was originally the objects that handled the "repeats".
    It remains mostly for nostlagic purposes and might disappear for a better name later on :)
'''

import os
import json
from datetime import datetime
import traceback

from modules.ui import plaintext_to_html
from modules.shared import opts

from .. import context as c
from ..payload import create_payloads

from .sd import txt2img
from . import *


def update_context(inputs):
    def get_input(key):
        if key not in COMPONENT_ARG_ORDER:
            return inputs[len(COMPONENT_ARG_ORDER):]
        return inputs[COMPONENT_ARG_ORDER.index(key)]

    c.init()
    c.tags = [tag.strip() for tag in get_input(TAGS).split(',')]
    c.model = get_input(MODEL)
    c.hr = get_input(USE_HIRES)
    c.restore = get_input(RESTORE_F)
    c.upscaler = get_input(UPSCALER) or c.upscaler
    c.scenario = get_input(SCENARIO)
    c.cfg_scale = get_input(CFG_SCALE) if get_input(USE_CFG_SCALE) else None
    c.nb_repeats = get_input(NB_REPEATS)
    c.nb_batches = get_input(NB_BATCHES)
    c.nb_iter = get_input(NB_ITER)
    c.sampler = get_input(SAMPLER) if get_input(USE_SAMPLER) else None
    c.steps = get_input(STEPS) if get_input(USE_STEPS) else None
    c.denoising_strength = get_input(DENOISE_ST)
    c.upscale_by = get_input(UPSCALE_BY)
    c.seed = get_input(SEED)
    c.positive = get_input(POSITIVE)
    c.negative = get_input(NEGATIVE)
    characters = get_input(CHARACTERS)
    c.chars = [characters[idx] for idx in c.expected_characters_idxs]


def bobing(_, *inputs):
    update_context(inputs)
    def get_input(key):
        return inputs[COMPONENT_ARG_ORDER.index(key)]

    if get_input(USE_CLIP_SKIP):
        old_clip_skip_value = opts.CLIP_stop_at_last_layers
        opts.CLIP_stop_at_last_layers = int(get_input(CLIP_SKIP))

    gallery = []
    first_gen = None
    try:
        for payload in create_payloads():
            if c.hard_skip_toggled:
                c.hard_skip_toggled = False
                break

            txt2img_gallery, generation_info, html_info, html_log = txt2img(payload)
            first_gen = first_gen or generation_info
            gallery += txt2img_gallery


            date = datetime.today().strftime('%Y-%m-%d')
            samples_dir = opts.outdir_txt2img_samples + '/' + date
            last_file_name = sorted(os.listdir(samples_dir))[-1].split('.')[0]

            model = payload['override_settings']['sd_model_checkpoint']
            with open(f'{samples_dir}/{last_file_name}a - {model}.json', 'w', encoding='utf-8') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4)
    except:
        print(traceback.format_exc())

    if get_input(USE_CLIP_SKIP):
        opts.CLIP_stop_at_last_layers = old_clip_skip_value

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')
