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

from .sd import data2img
from .constants import * # pylint: disable=wildcard-import


def update_context(inputs):
    def get_character_data():
        nb_char = len(c.database['character_types'])
        start_chars = len(COMPONENT_ARG_ORDER)
        start_prompts = start_chars + nb_char
        start_weights = start_prompts + nb_char
        start_comopts = start_weights + nb_char
        return (
            inputs[start_chars:start_prompts],
            inputs[start_prompts:start_weights],
            inputs[start_weights:start_comopts],
            inputs[start_comopts:],
        )
    def get_input(key):
        if key not in COMPONENT_ARG_ORDER:
            return get_character_data()
        return inputs[COMPONENT_ARG_ORDER.index(key)]

    c.init()
    c.styles = get_input(STYLES)
    c.model = get_input(MODEL)
    c.hr = get_input(USE_HIRES)
    c.restore = get_input(RESTORE_F)
    c.ad = get_input(USE_AD)
    c.fe = get_input(USE_FE)
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
    c.use_clip_skip = get_input(USE_CLIP_SKIP)
    c.clip_skip = get_input(CLIP_SKIP)
    c.enable_models_presets = get_input(ENABLE_MODELS_PRESETS)
    characters, char_prompts, char_weights, char_comopts = get_input(CHARACTERS)
    c.chars = [characters[idx] for idx in c.expected_characters_idxs]
    c.char_prompts = [char_prompts[idx] for idx in c.expected_characters_idxs]
    c.char_weights = [char_weights[idx] for idx in c.expected_characters_idxs]
    c.char_comopts = [char_comopts[idx] for idx in c.expected_characters_idxs]


def bobing(_, *inputs):
    update_context(inputs)
    if c.scenario in c.database.get('pages', {}):
        return bobing_page()

    gallery = []
    first_gen = None
    try:
        for payload in create_payloads():
            if c.hard_skip_toggled:
                c.hard_skip_toggled = False
                break

            try:
                txt2img_gallery, generation_info, html_info, html_log = data2img(payload)
                first_gen = first_gen or generation_info
                gallery += txt2img_gallery
            except IndexError:
                print('Could not update gallery')


            date = datetime.today().strftime('%Y-%m-%d')
            samples_dir = opts.outdir_txt2img_samples + '/' + date
            last_file_name = sorted([file_ for file_ in os.listdir(samples_dir) if file_.endswith('.png')])[-1].split('.')[0]

            model = payload['override_settings']['sd_model_checkpoint']
            with open(f'{samples_dir}/{last_file_name}a - {model}.json', 'w', encoding='utf-8') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4, default=lambda _: 'Non serializable, ignored')
    except:
        print(traceback.format_exc())

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')

def bobing_page():
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

            try:
                txt2img_gallery, generation_info, html_info, html_log = data2img(payload)
                first_gen = first_gen or generation_info
                gallery += txt2img_gallery
                sc_imgs += txt2img_gallery[:last_batch_size]
            except IndexError:
                print('Could not update gallery')

            date = datetime.today().strftime('%Y-%m-%d')
            samples_dir = opts.outdir_txt2img_samples + '/' + date
            last_file_name = sorted([file_ for file_ in os.listdir(samples_dir) if file_.endswith('.png')])[-1].split('.')[0]

            model = payload['override_settings']['sd_model_checkpoint']
            with open(f'{samples_dir}/{last_file_name}b - {model}.json', 'w', encoding='utf-8') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4, default=lambda _: 'Non serializable, ignored')
    except:
        print(traceback.format_exc())

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')