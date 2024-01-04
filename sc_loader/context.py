'''
    A rather crappy but useful module to handle global variables, should be reworked.
'''

import os

from modules.shared import opts
from modules import scripts

from .config import load_dir_element

version = '6.0.0'


database      = None
scenario      = None
batch         = None
styles        = None
hr            = False
restore       = False
fe            = False
ad            = False
upscaler      = None
chars         = None
char_prompts  = None
char_weights  = None
char_comopts  = None
sampler       = None
steps         = None
characters    = None
cfg_scale     = None
model         = None
nb_iter       = None
nb_batches    = None
nb_repeats    = None
positive      = None
negative      = None
upscale_by    = None
use_clip_skip = None
clip_skip     = None
seed          = -1
denoise_args  = None
current_payload    = None
skipped_model      = None
hard_skip_toggled  = None
denoising_strength = None
expected_characters_idxs = []
poses_masks_generated = []
enable_models_presets = False

skip_model = False

short_prompts = {'positive': '', 'negative': ''}

DB_DIR = '_db'

warned = False
default_path = os.path.join(scripts.current_basedir, 'base_configs')

def prefix(file_name):
    return ''.join((part[0:4] for part in file_name.split('_')))

def warn(msg):
    global warned
    if not warned:
        print('[SC LOADER][WARNING] >>>> ', msg)
        print('[SC LOADER][WARNING] >>>> ', msg)
        print('[SC LOADER][WARNING] >>>> ', msg)
        warned = True

def get_cfg_path():
    global default_path
    try:
        if not os.path.exists(opts.sc_loader_config_path):
            warn(f'Could not load DB, using default one at {default_path}, you can change it in tools or settings.')
            return default_path
        return opts.sc_loader_config_path
    except:
        warn(f'Could not load DB, using default one at {default_path}, you can change it in tools or settings.')
        return default_path

def load_db():
    global database
    database = load_dir_element(f'{get_cfg_path()}/{DB_DIR}')
    path_to_types = f'{get_cfg_path()}/{DB_DIR}/prompts'
    for file_name in os.listdir(path_to_types):
        if os.path.isdir(path_to_types + '/' + file_name) and file_name[0] != '_':
            for key, value in database['prompts'][file_name].items():
                database['prompts'][prefix(file_name)+'_'+key] = value

def skip():
    global skipped_model, skip_model
    skip_model = True
    skipped_model = current_payload['override_settings']['sd_model_checkpoint'] # pylint: disable=unsubscriptable-object

def init():
    global scenario, batch, styles, hr, restore, upscaler, chars, sampler, steps, characters,\
            cfg_scale, model, nb_iter, nb_batches, nb_repeats, seed, positive, negative,\
            denoising_strength, upscale_by, hard_skip_toggled, current_payload,\
            skipped_model, char_prompts, use_clip_skip, clip_skip, enable_models_presets,\
            char_weights, char_comopts, fe, ad
    load_db()
    scenario      = None
    batch         = None
    styles        = None
    hr            = False
    restore       = False
    fe            = False
    ad            = False
    upscaler      = None
    chars         = None
    char_prompts  = None
    char_weights  = None
    char_comopts  = None
    sampler       = None
    steps         = None
    characters    = None
    cfg_scale     = None
    model         = None
    nb_iter       = None
    nb_batches    = None
    nb_repeats    = None
    positive      = None
    negative      = None
    upscale_by    = None
    use_clip_skip = None
    clip_skip     = None
    seed          = -1
    current_payload    = None
    skipped_model      = None
    hard_skip_toggled  = None
    denoising_strength = None
    enable_models_presets = False
