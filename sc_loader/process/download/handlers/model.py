import traceback

from .... import context as c

from ..url import url_data
from ..civitai import model_data, download_model
from ..prompt import build_data
from ..db import add_prompt

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
