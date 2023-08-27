import traceback

from ... import context as c

from .url import url_data
from .civitai import model_data, download_model, download_wildcards
from .prompt import build_data
from .db import add_prompt, get_wildcard_path

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
def handle_model(sc_file, name, civitai_url, prompt, weight, prompt_type): # pylint: disable=too-many-arguments,too-many-locals
    type_ = prompt_type[:-1]
    c.load_db()
    print(f'Adding {type_} {name}')
    if name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({name}) already exists')

    model_id, pids, version = url_data(type_, civitai_url)
    data, model, model_file = model_data(model_id, version)
    model_type, prompt, file_path, download_url = build_data(name, data, model, model_file, pids, prompt, weight)
    if model_type != 'wildcard':
        download_model(download_url, file_path, type_)
        if model_type != 'ckpt':
            add_prompt(sc_file, name, prompt, prompt_type, type_)
    else:
        download_wildcards(download_url, get_wildcard_path(data, prompt_type))
