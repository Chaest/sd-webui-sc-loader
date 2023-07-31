import os
import re
import traceback

import requests

from modules.shared import opts

from .. import context as c
from ..context import DB_DIR

TYPE_MAPPER = {
    'LORA': 'lora',
    'LoCon': 'lyco',
    'TextualInversion': 'TextualInversion'
}
TYPE_TO_FOLDER = {
    'lora': 'Lora',
    'lyco': 'LyCORIS'
}

def output_result(f):
    def outputter(*args):
        msg = f'Successfully added {args[5][:-1]} {args[1]}'
        try:
            f(*args)
        except:
            msg = traceback.format_exc()
            print(msg)
        return msg.replace('\n', '<br>')
    return outputter

@output_result
def create_character(sc_file, name, civitai_url, prompt, weight, prompt_type): # pylint: disable=too-many-arguments,too-many-locals
    type_ = prompt_type[:-1]
    c.load_db()
    print(f'Adding {type_} {name}')
    if name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({name}) already exists')

    model_id, pids, version = get_ids(type_, civitai_url)
    model_data, version_data, file_data = get_model_data(model_id, version)
    char_data, file_path, download_url = build_data(name, model_data, version_data, file_data, pids, prompt, weight)
    download_model(download_url, file_path, type_)
    add_prompt(sc_file, name, char_data, prompt_type, type_)

def get_ids(type_, civitai_url):
    print(f'Starting {type_} creation')
    civitai_url_regex = r'https://civitai\.com/models/(?P<id>\d+)(/[^\[]+)?(\[(?P<pids>\d+(,\d+)*)\])?(@(?P<version>\d+))?'
    m = re.match(civitai_url_regex, civitai_url)
    if not m:
        raise Exception(f'URL ({civitai_url}) is not valid')

    url_data = m.groupdict()
    model_id = url_data['id']
    pids_str = url_data.get('pids')
    version_str = url_data.get('version')
    pids = [int(pid) for pid in pids_str.split(',')] if pids_str else []
    version = int(version_str) if version_str else 0
    print(f'Selected prompts: {pids}')
    print(f'Selected version: {version}')
    return model_id, pids, version

def get_model_data(model_id, version):
    print(f'Getting model {model_id}')
    response = requests.get(f'https://civitai.com/api/v1/models/{model_id}', timeout=30)
    content = response.json()
    model_version = content['modelVersions'][version]
    version_model_file = model_version['files'][0]
    if version_model_file['type'] != 'Model':
        if len(model_version['files']) > 1:
            print('First file was invalid:', version_model_file['type'])
            print('Trying second file')
            version_model_file = model_version['files'][1]
            if version_model_file['type'] != 'Model':
                raise Exception('Invalid model type:', version_model_file['type'])
        else:
            raise Exception('Invalid model type:', version_model_file['type'])
    if model_version['baseModel'] not in ('SD 1.4', 'SD 1.5', 'Other'):
        raise Exception('Invalid base model:', model_version['baseModel'])
    return content, model_version, version_model_file

def build_data(name, model, version, file_data, pids, prompt, weight): # pylint: disable=too-many-arguments
    print('Building data')
    model_type = TYPE_MAPPER[model['type']]
    file_hash = file_data['hashes'].get('AutoV2', model['creator'].get('username', 'wtf'))
    download_url = file_data['downloadUrl']

    if model_type == 'TextualInversion':
        file_name = file_data['name'].replace('.pt', '_' + file_hash)
        trained_words = f'({file_name}:{weight})'
        if prompt:
            trained_words += ', ' + prompt
        trained_words = trained_words.replace('\\', '\\\\').strip()
        char_data = f'\n{name}: {trained_words}\n'
        file_path = f'embeddings/{file_name}.pt'
    else:
        trained_words = ', '.join([trained_word for idx, trained_word in enumerate(version['trainedWords']) if not pids or idx in pids])
        if prompt:
            trained_words += ', ' + prompt
        trained_words = trained_words.replace('\\', '\\\\').strip()
        file_name = file_data['name'].replace('.safetensors', '_' + file_hash)
        char_data = f'\n{name}: >-\n  {trained_words}, <{model_type}:{file_name}:{weight}>\n'
        file_path = f'models/{TYPE_TO_FOLDER[model_type]}/{file_name}.safetensors'

    return char_data, file_path, download_url

def download_model(download_url, file_path, type_):
    print(f'Downloading {type_}')
    response = requests.get(download_url, stream=True, timeout=30)
    response.raise_for_status()
    model_path = f'{os.getcwd()}/{file_path}'
    print('Destination:', model_path)
    if not os.path.exists(model_path):
        with open(model_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8192):
                fd.write(chunk)
    else:
        print('Model already present')
    print(f'{type_.capitalize()} downloaded')

def add_prompt(sc_file, name, prompt, prompt_type, type_):
    path_to_file = f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/{prompt_type}/{sc_file}'
    print(f'Adding {type_} prompt to ({path_to_file})')
    with open(path_to_file, 'a', encoding='utf-8') as sc_fd:
        sc_fd.write(prompt)
    print(f'{type_.capitalize()} {name} added')
