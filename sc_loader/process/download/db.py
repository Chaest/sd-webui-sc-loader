from modules.shared import opts

from ...context import DB_DIR
from .utils import normalized_name

def add_prompt(sc_file, name, prompt, prompt_type, type_):
    path_to_file = f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/{prompt_type}/{sc_file}'
    print(f'Adding {type_} prompt to ({path_to_file})')
    with open(path_to_file, 'a', encoding='utf-8') as sc_fd:
        sc_fd.write(prompt)
    print(f'{type_.capitalize()} {name} added')

def get_wildcard_path(civitai_data):
    return f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/wild_cards/_wc_' + normalized_name(civitai_data['name'])

def get_poses_path(civitai_data):
    return f'{opts.sc_loader_config_path}/poses/' + normalized_name(civitai_data['name'])

def get_batches_path(batch_name):
    return f'{opts.sc_loader_config_path}/{DB_DIR}/batches/{batch_name}.txt'
