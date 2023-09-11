import traceback

from ..url import url_data
from ..civitai import model_data, download_wildcards, download_base_model, download_poses, download_package
from ..prompt import build_data
from ..db import get_wildcard_path, get_poses_path, get_package_path

def output_result(f):
    def outputter(*args):
        try:
            msg = f(*args)
        except:
            msg = 'ERROR \n' + traceback.format_exc()
            print(msg)
        return msg.replace('\n', '<br>')
    return outputter

@output_result
def handle_wildcards(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding wild cards')

    model_id, pids, version = url_data('wild_cards', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'wildcard':
        raise Exception('Not a wildcards')
    download_wildcards(download_url, get_wildcard_path(data))
    return 'Successfully downloaded wildcards'

@output_result
def handle_poses(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding poses')

    model_id, pids, version = url_data('poses', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'Poses':
        raise Exception('Not a poses')
    download_poses(download_url, get_poses_path(data))
    return 'Successfully downloaded poses'

@output_result
def handle_base_model(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding model')

    model_id, pids, version = url_data('model', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, file_path, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'ckpt':
        raise Exception('Not a model')
    download_base_model(download_url, file_path)
    return 'Successfully downloaded base model'

@output_result
def handle_package(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding package')

    model_id, pids, version = url_data('model', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, file_path, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'Package':
        raise Exception('Not a package')
    download_package(download_url, get_package_path(data))
    return 'Successfully downloaded package'

MODEL_TYPE_TO_HANLDER = {
    'wildcard': handle_wildcards,
    'ckpt': handle_base_model,
    'Poses': handle_poses,
    'Package': handle_package
}

def generic_handler(civitai_url): # pylint: disable=too-many-locals
    model_id, pids, version = url_data('generic', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, _ = build_data('', data, model, model_file, pids, '', '', 0)
    return MODEL_TYPE_TO_HANLDER[model_type](civitai_url)
