import traceback

from .... import context as c

from ..url import url_data
from ..civitai import CivitAIModel
from ..prompt import create_prompt
from ..db import add_prompt
from ..utils import normalized_name

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
def handle_model(sc_file, name, civitai_url, user_prompt, negative_prompt, weight, prompt_type): # pylint: disable=too-many-arguments,too-many-locals
    type_ = prompt_type[:-1]
    c.load_db()
    print(f'Adding {type_} {name}')
    if name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({name}) already exists')

    model_id, pids, version = url_data(type_, civitai_url)
    model = CivitAIModel(model_id, version)

    name = (name if name != '_' else normalized_name(model.name))
    if name in c.database['prompts'][prompt_type]:
        raise Exception(f'{type_.capitalize()} ({name}) already exists')

    prompt = create_prompt(name, model, weight, user_prompt, negative_prompt, pids)
    if model.type in ('ckpt', 'wildcards'):
        raise Exception('Please use tools for wildcards or base model download')
    model.download()

    add_prompt(sc_file, name, prompt, prompt_type, type_)

    return name
