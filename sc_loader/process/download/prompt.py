import os

from sc_loader.process.sd import basemodels_dir, lora_dir, lyco_dir, embeddings_dir

from .utils import normalized_name
from ... import context as c

TYPE_MAPPER = {
    'LORA': 'lora',
    'LoCon': 'lyco',
    'TextualInversion': 'ti',
    'Checkpoint': 'ckpt',
    'Wildcards': 'wildcard',
    'Poses': 'Poses',
    'Other': 'Package'
}
TYPE_TO_FOLDER = {
    'lora': lora_dir(),
    'lyco': lyco_dir(),
    'ckpt': basemodels_dir(),
    'ti': embeddings_dir(),
    'wildcard': 'N/A',
    'Poses': 'N/A',
    'Package': 'N/A'
}

def build_data(name, model, version, file_data, pids, user_prompt, negative_prompt, weight): # pylint: disable=too-many-arguments
    print('Building data')
    model_type = TYPE_MAPPER[model['type']]
    file_name, file_path, download_url = download_data(model, model_type, file_data)
    model_prompt = create_model_prompt(model_type, weight, file_name)
    actual_name = (name if name != '_' else normalized_name(model['name']))
    prompt = create_prompt(download_url, actual_name, user_prompt, negative_prompt, version, pids, model_prompt)

    return actual_name, model_type, prompt, file_path, download_url

def create_prompt(url, name, user_prompt, negative_prompt, version, pids, model_prompt):
    prompts = version.get('trainedWords', [])
    if pids:
        prompts = [prompt for idx, prompt in enumerate(prompts) if idx in pids]
    if user_prompt:
        prompts.append(user_prompt)
    prompts.append(model_prompt)
    prompts = ', '.join(prompts).replace('\\', '\\\\').strip()
    prompts = clean_prompt(prompts)
    if not negative_prompt:
        return f'\n# Download URL: {url}\n{name}: >-\n  {prompts}\n'
    negative_prompt = clean_prompt(negative_prompt)
    return f'\n# Download URL: {url}\n{name}:\n  - >-\n    {prompts}\n  - {negative_prompt}\n'

def download_data(model, type_, file_data):
    file_hash = file_data['hashes'].get('AutoV2', model['creator'].get('username', 'undefined'))
    download_url = file_data['downloadUrl']
    file_name_wo_ext, file_name = specific_name(file_data['name'], file_hash)
    file_path = os.path.join(TYPE_TO_FOLDER[type_], file_name)
    return file_name_wo_ext, file_path, download_url

def create_model_prompt(model_type, weight, file_name):
    if model_type == 'ti':
        if weight == 1:
            return file_name
        if weight == 1.1: # for the sake of beauty
            return f'({file_name})'
        if weight == 1.2: # for the sake of beauty
            return f'(({file_name}))'
        return f'({file_name}:{weight})'
    if model_type in ('lora', 'lyco'):
        return f'<{model_type}:{file_name}:{weight}>'
    return ''

def specific_name(filename, hash_):
    base_name, ext = os.path.splitext(filename)
    hashed_name = f'{base_name}_{hash_}'
    return hashed_name, f'{hashed_name}{ext}'

def clean_prompt(prompt):
    blacklist = []
    if 'prompts_blacklist' in c.database:
        blacklist = c.database['prompts_blacklist']
        if not isinstance(blacklist, list):
            print('[ERROR] Blacklist should be a list')
            blacklist = []

    for blacklisted_prompt in blacklist:
        prompt = prompt.replace(blacklisted_prompt, '')

    prompt = prompt.replace(',', ', ')
    while '  ' in prompt: prompt = prompt.replace('  ', ' ')
    while ', ,' in prompt: prompt = prompt.replace(', ,', ',')
    while ',,' in prompt: prompt = prompt.replace(',,', ',')
    if prompt.startswith(', '): prompt = prompt[2:]

    return prompt
