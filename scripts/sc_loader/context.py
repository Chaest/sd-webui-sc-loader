from .config import DB_PATH, load_cfg

database   = None
scenario   = None
sc_data    = None
batch      = None
tags       = []
batch_data = None
hr         = False
restore    = False
upscaler   = 'esrgan'
chars      = None
sampler    = None
steps      = None
characters = None
cfg_scale  = None
model      = None

c = {}
short_prompts = {'positive': '', 'negative': ''}
version = '2.0.0'

def load_db(current_directory):
    global database
    database = load_cfg(current_directory +'/' + DB_PATH)

def init(current_directory):
    global scenario, batch, tags, batch_data, hr, restore, upscaler, chars, sampler, steps, characters, cfg_scale, model
    load_db(current_directory)
    scenario   = None
    sc_data    = None
    batch      = None
    tags       = []
    batch_data = None
    hr         = False
    restore    = False
    upscaler   = 'esrgan'
    chars      = None
    sampler    = None
    steps      = None
    characters = None
    cfg_scale  = None
    model      = None