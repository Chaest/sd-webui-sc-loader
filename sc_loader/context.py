'''
    A rather crappy but useful module to handle global variables, should be reworked.
'''

import os
from distutils.dir_util import copy_tree

from modules.shared import opts
from modules import scripts

from .config import load_dir_element

version = '5.1.0'


database     = None
scenario     = None
batch        = None
style        = None
hr           = False
restore      = False
upscaler     = None
chars        = None
char_prompts = None
sampler      = None
steps        = None
characters   = None
cfg_scale    = None
model        = None
nb_iter      = None
nb_batches   = None
nb_repeats   = None
positive     = None
negative     = None
upscale_by   = None
seed         = -1
denoise_args = None
current_payload    = None
skipped_model      = None
hard_skip_toggled  = None
denoising_strength = None
expected_characters_idxs = []
poses_masks_generated = []

skip_model = False

short_prompts = {'positive': '', 'negative': ''}

DB_DIR = '_db'

warned = False

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
    default_path = os.path.join(scripts.current_basedir, 'sc_configs')
    try:
        if not os.path.exists(opts.sc_loader_config_path):
            if not os.path.exists(default_path):
                copy_tree('extensions/sd-webui-sc-loader/base_configs', default_path)
                warn(f'Could not load DB, created a new one default one at {default_path}, you can change it in tools or settings.')
            else:
                warn(f'Could not load DB, using default one at {default_path}, you can change it in tools or settings.')
            return default_path
        return opts.sc_loader_config_path
    except:
        if not os.path.exists(default_path):
            copy_tree('extensions/sd-webui-sc-loader/base_configs', default_path)
            warn(f'Initiated a DB at {default_path}, you can change it in tools or settings.')
        else:
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
    global scenario, batch, style, hr, restore, upscaler, chars, sampler, steps, characters,\
            cfg_scale, model, nb_iter, nb_batches, nb_repeats, seed, positive, negative,\
            denoising_strength, upscale_by, hard_skip_toggled, current_payload,\
            skipped_model, char_prompts
    load_db()
    scenario     = None
    batch        = None
    style        = None
    hr           = False
    restore      = False
    upscaler     = None
    chars        = None
    char_prompts = None
    sampler      = None
    steps        = None
    characters   = None
    cfg_scale    = None
    model        = None
    nb_iter      = None
    nb_batches   = None
    nb_repeats   = None
    positive     = None
    negative     = None
    upscale_by   = None
    seed         = -1
    current_payload    = None
    skipped_model      = None
    hard_skip_toggled  = None
    denoising_strength = None
