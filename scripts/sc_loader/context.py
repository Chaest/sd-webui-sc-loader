import os

from modules.shared import opts

from .config import load_dir_element

database   = None
scenario   = None
batch      = None
tags       = []
hr         = False
restore    = False
upscaler   = None
chars      = None
sampler    = None
steps      = None
characters = None
cfg_scale  = None
model      = None
nb_iter    = None
nb_batches = None
nb_repeats = None
positive   = None
negative   = None
seed       = -1

skip_model = False

short_prompts = {'positive': '', 'negative': ''}
version = '3.3.0'

def load_db():
    global database
    database = load_dir_element(opts.sc_loader_config_path + '/db', True)
    path_to_types = f'{opts.sc_loader_config_path}/db/prompts'
    for file_name in os.listdir(path_to_types):
        if os.path.isdir(path_to_types + '/' + file_name):
            suffix = ''.join((part[0] for part in file_name.split('_')))
            for key, value in database['prompts'][file_name].items():
                database['prompts'][suffix+'_'+key] = value

def init():
    global scenario, batch, tags, hr, restore, upscaler, chars, sampler, steps, characters,\
            cfg_scale, model, nb_iter, nb_batches, nb_repeats, seed, positive, negative
    load_db()
    scenario   = None
    batch      = None
    tags       = []
    hr         = False
    restore    = False
    upscaler   = None
    chars      = None
    sampler    = None
    steps      = None
    characters = None
    cfg_scale  = None
    model      = None
    nb_iter    = None
    nb_batches = None
    nb_repeats = None
    positive   = None
    negative   = None
    seed       = -1