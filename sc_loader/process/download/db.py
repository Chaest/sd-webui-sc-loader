from modules.shared import opts

from ...context import DB_DIR

def add_prompt(sc_file, name, prompt, prompt_type, type_):
    path_to_file = f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/{prompt_type}/{sc_file}'
    print(f'Adding {type_} prompt to ({path_to_file})')
    with open(path_to_file, 'a', encoding='utf-8') as sc_fd:
        sc_fd.write(prompt)
    print(f'{type_.capitalize()} {name} added')

def get_wildcard_path(civitai_data, prompt_type):
    return f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/{prompt_type}/_wc_' + civitai_data['name'].replace(' ', '_')
