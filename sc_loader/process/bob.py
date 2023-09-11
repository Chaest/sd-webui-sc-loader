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
from ..payload import create_payloads, create_payloads_for_page
from sc_loader.process.page import generate_pages

from .sd import txt2img
from . import * # pylint: disable=wildcard-import


def update_context(inputs):
    def get_input(key):
        if key not in COMPONENT_ARG_ORDER:
            characters_data = inputs[len(COMPONENT_ARG_ORDER):]
            middle = int(len(characters_data) / 2)
            return characters_data[:middle], characters_data[middle:]
        return inputs[COMPONENT_ARG_ORDER.index(key)]

    c.init()
    c.style = get_input(STYLE)
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
    characters, char_prompts = get_input(CHARACTERS)
    c.chars = [characters[idx] for idx in c.expected_characters_idxs]
    c.char_prompts = [char_prompts[idx] for idx in c.expected_characters_idxs]


def bobing(_, *inputs):
    update_context(inputs)
    def get_input(key):
        return inputs[COMPONENT_ARG_ORDER.index(key)]
    if c.scenario in c.database.get('pages', {}):
        return bobing_page(int(get_input(CLIP_SKIP)) if get_input(USE_CLIP_SKIP) else None)

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
            last_file_name = sorted([file_ for file_ in os.listdir(samples_dir) if file_.endswith('.png')])[-1].split('.')[0]

            model = payload['override_settings']['sd_model_checkpoint']
            with open(f'{samples_dir}/{last_file_name}a - {model}.json', 'w', encoding='utf-8') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4, default=lambda _: 'Non serializable, ignored')
    except:
        print(traceback.format_exc())

    if get_input(USE_CLIP_SKIP):
        opts.CLIP_stop_at_last_layers = old_clip_skip_value

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')

def bobing_page(clip_skip):
    if clip_skip:
        old_clip_skip_value = opts.CLIP_stop_at_last_layers
        opts.CLIP_stop_at_last_layers = clip_skip

    gallery = []
    sc_imgs = []
    first_gen = None
    page = c.database['pages'][c.scenario]
    last_batch_size = 0
    try:
        for payload in create_payloads_for_page():
            if c.hard_skip_toggled:
                c.hard_skip_toggled = False
                break

            if payload is None:
                try:
                    pages, pages_with_text = generate_pages(page, sc_imgs, last_batch_size)
                    # Too performance heavy
                    #gallery += pages
                    #gallery += pages_with_text
                    date = datetime.today().strftime('%Y-%m-%d')
                    samples_dir = opts.outdir_txt2img_samples + '/' + date
                    last_file_name = sorted([file_ for file_ in os.listdir(samples_dir) if file_.endswith('.png')])[-1].split('.')[0]
                    for i, img in enumerate(pages + pages_with_text):
                        img.save(f'{samples_dir}/{last_file_name}a{i} - {model}.jpg')
                    sc_imgs = []
                except:
                    print(traceback.format_exc())
                    sc_imgs = []
                continue

            last_batch_size = payload['batch_size'] * payload['n_iter']

            txt2img_gallery, generation_info, html_info, html_log = txt2img(payload)
            first_gen = first_gen or generation_info
            gallery += txt2img_gallery
            sc_imgs += txt2img_gallery[:last_batch_size]

            date = datetime.today().strftime('%Y-%m-%d')
            samples_dir = opts.outdir_txt2img_samples + '/' + date
            last_file_name = sorted([file_ for file_ in os.listdir(samples_dir) if file_.endswith('.png')])[-1].split('.')[0]

            model = payload['override_settings']['sd_model_checkpoint']
            with open(f'{samples_dir}/{last_file_name}b - {model}.json', 'w', encoding='utf-8') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4, default=lambda _: 'Non serializable, ignored')
    except:
        print(traceback.format_exc())

    if clip_skip:
        opts.CLIP_stop_at_last_layers = old_clip_skip_value

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')