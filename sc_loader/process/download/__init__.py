import traceback

from ... import context as c

from .url import url_data
from .civitai import model_data, download_model, download_wildcards, download_base_model, download_poses
from .prompt import build_data
from .db import add_prompt, get_wildcard_path, get_poses_path, get_batches_path
from .utils import normalized_name

def output_result(f):
    def outputter(*args):
        msg = f'Successfully added {args[-1][:-1]} {args[1]}'
        try:
            name = f(*args)
            if args[1] == '_':
                msg = msg[:-1] + ' ' + name
        except:
            msg = 'ERROR \n' + traceback.format_exc()
            print(msg)
        return msg.replace('\n', '<br>')
    return outputter

def output_result_mono(f):
    def outputter(*args):
        try:
            msg = f(*args)
        except:
            msg = 'ERROR \n' + traceback.format_exc()
            print(msg)
        return msg.replace('\n', '<br>')
    return outputter

@output_result
def handle_model(sc_file, name, civitai_url, prompt, negative_prompt, weight, prompt_type): # pylint: disable=too-many-arguments,too-many-locals
    type_ = prompt_type[:-1]
    c.load_db()
    print(f'Adding {type_} {name}')
    if name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({name}) already exists')

    model_id, pids, version = url_data(type_, civitai_url)
    data, model, model_file = model_data(model_id, version)
    actual_name, model_type, prompt, file_path, download_url = build_data(name, data, model, model_file, pids, prompt, negative_prompt, weight)
    if name != actual_name and actual_name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({actual_name}) already exists')
    if model_type in ('ckpt', 'wildcards'):
        raise Exception('Please use tools for wildcards or base model download')
    download_model(download_url, file_path, type_)
    add_prompt(sc_file, actual_name, prompt, prompt_type, type_)
    return actual_name

@output_result_mono
def handle_wildcards(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding wild cards')

    model_id, pids, version = url_data('wild_cards', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'wildcard':
        raise Exception('Not a wildcards')
    download_wildcards(download_url, get_wildcard_path(data))
    return 'Successfully download wildcards'

@output_result_mono
def handle_poses(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding poses')

    model_id, pids, version = url_data('poses', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'Poses':
        raise Exception('Not a poses')
    download_poses(download_url, get_poses_path(data))
    return 'Successfully download poses'

@output_result_mono
def handle_base_model(civitai_url): # pylint: disable=too-many-locals
    print(f'Adding model')

    model_id, pids, version = url_data('model', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, file_path, download_url = build_data('', data, model, model_file, pids, '', '', 0)
    if model_type != 'ckpt':
        raise Exception('Not a model')
    download_base_model(download_url, file_path)
    return 'Successfully download base model'

MODEL_TYPE_TO_HANLDER = {
    'wildcard': handle_wildcards,
    'ckpt': handle_base_model,
    'Poses': handle_poses
}

def generic_handler(civitai_url): # pylint: disable=too-many-locals
    model_id, pids, version = url_data('generic', civitai_url)
    data, model, model_file = model_data(model_id, version)
    _, model_type, _, _, _ = build_data('', data, model, model_file, pids, '', '', 0)
    return MODEL_TYPE_TO_HANLDER[model_type](civitai_url)

def handle_batch(batch_name):
    with open(get_batches_path(batch_name), 'r', encoding='utf-8') as f:
        lines = f.readlines()

    batch_elements = []
    batch_idx = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('> '):
            if batch_idx-1 >= 0:
                batch_elements[batch_idx-1].append(line[2:])
        else:
            batch_idx += 1
            batch_elements.append([line])

    batches_results = ''
    for batch_element in batch_elements:
        try:
            msg = batch_line_handler(*batch_element)
            if msg.startswith('ERROR'):
                msg = msg.replace('<br>', '\n').strip().split('\n')[-1]
                batches_results += f'Failed ({msg})\n'
            else:
                batches_results += 'Success\n'
        except Exception as e:
            batches_results += f'Failed ({e})\n'
    return batches_results.replace('\n', '<br>')

def batch_line_handler(batch_line, batch_pos_line=None, batch_neg_line=None):
    while '  ' in batch_line: batch_line = batch_line.replace('  ', ' ')
    elements = batch_line.split(' ')
    if len(elements) == 1:
        return generic_handler(elements[0])
    prompt_type, sc_file = elements[1].split('/')

    weight = 0.75
    name = '_'
    if len(elements) > 2:
        try:
            weight = float(elements[2])
        except:
            name = elements[2]
    if len(elements) > 3:
        try:
            weight = float(elements[3])
        except:
            if name != '_':
                raise Exception(f'Invalid batch line {batch_line}')
            name = elements[3]

    return handle_model(sc_file, name, elements[0], batch_pos_line or '', batch_neg_line or '', weight, prompt_type)
