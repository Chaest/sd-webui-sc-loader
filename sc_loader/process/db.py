import os
from distutils.dir_util import copy_tree

from modules.shared import opts

from ..context import DB_DIR, get_cfg_path

def copy_db(new_path):
    new_path += '/sc_config'
    try:
        copy_tree('extensions/sd-webui-sc-loader/base_configs', new_path)
        opts.sc_loader_config_path = new_path
        return f'Successfully created DB at {new_path}'
    except:
        return 'Could not create DB, ensure you\'ve got rights and path exists'

def add_file_to_db(new_path):
    new_path = f'{get_cfg_path()}/{DB_DIR}/prompts/{new_path}'

    if os.path.exists(new_path):
        return f'File already exists at {new_path}'

    directory = os.path.dirname(new_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        with open(new_path, 'w'):
            pass
        return f'Successfully created an empty file at {new_path}'
    except:
        return 'Could not create file, ensure you\'ve got rights and path exists'
