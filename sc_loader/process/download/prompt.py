import os

TYPE_MAPPER = {
    'LORA': 'lora',
    'LoCon': 'lyco',
    'TextualInversion': 'ti',
    'Checkpoint': 'ckpt',
    'Wildcards': 'wildcard'
}
TYPE_TO_FOLDER = {
    'lora': 'models/Lora',
    'lyco': 'models/LyCORIS',
    'ckpt': 'models/Stable-diffusion',
    'ti': 'embeddings',
    'wildcard': 'N/A'
}

def build_data(name, model, version, file_data, pids, user_prompt, weight): # pylint: disable=too-many-arguments
    print('Building data')
    model_type = TYPE_MAPPER[model['type']]
    file_name, file_path, download_url = download_data(model, model_type, file_data)
    model_prompt = create_model_prompt(model_type, weight, file_name)
    prompt = create_prompt(name, user_prompt, version, pids, model_prompt)

    return model_type, prompt, file_path, download_url

def create_prompt(name, user_prompt, version, pids, model_prompt):
    prompts = version.get('trainedWords', [])
    if pids:
        prompts = [prompt for idx, prompt in enumerate(prompts) if idx in pids]
    if user_prompt:
        prompts.append(user_prompt)
    prompts.append(model_prompt)
    prompts = ', '.join(prompts).replace('\\', '\\\\').strip()
    return f'\n{name}: >-\n  {prompts}\n'

def download_data(model, type_, file_data):
    file_hash = file_data['hashes'].get('AutoV2', model['creator'].get('username', 'undefined'))
    download_url = file_data['downloadUrl']
    file_name_wo_ext, file_name = specific_name(file_data['name'], file_hash)
    file_path = TYPE_TO_FOLDER[type_] + '/' + file_name
    return file_name_wo_ext, file_path, download_url

def create_model_prompt(model_type, weight, file_name):
    if model_type == 'ti':
        if weight == 1:
            return file_name
        if weight == 1.1: # for the sake of beauty
            return f'({file_name})'
        return f'({file_name}:{weight})'
    if model_type in ('lora', 'lyco'):
        return f'<{model_type}:{file_name}:{weight}>'
    return ''

def specific_name(filename, hash):
    base_name, ext = os.path.splitext(filename)
    hashed_name = f'{base_name}_{hash}'
    return hashed_name, f'{hashed_name}{ext}'
