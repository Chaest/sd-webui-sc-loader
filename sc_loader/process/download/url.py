import re

CIVITAI_BASE_URL = 'https://civitai.com/models/'
MODEL_ID_REGEX_PART = r'(?P<id>\d+)(/[^\[]+)?'
PROMPT_INDEXES_REGEX_PART = r'(\[(?P<pids>\d+(,\d+)*)\])?'
VERSION_REGEX_PART = r'(@(?P<version>\d+))?'
URL_REGEX = rf'{CIVITAI_BASE_URL}{MODEL_ID_REGEX_PART}{PROMPT_INDEXES_REGEX_PART}{VERSION_REGEX_PART}'

def url_data_dict(civitai_url):
    m = re.match(URL_REGEX, civitai_url)
    if not m:
        raise Exception(f'URL ({civitai_url}) is not valid')
    return m.groupdict()

def url_data(type_, civitai_url):
    print(f'Starting {type_} creation')
    data = url_data_dict(civitai_url)

    model_id = data['id']
    pids_str = data.get('pids')
    version_str = data.get('version')

    pids = [int(pid) for pid in pids_str.split(',')] if pids_str else []
    version = int(version_str) if version_str else 0

    print(f'Selected prompts: {pids}')
    print(f'Selected version: {version}')

    return model_id, pids, version
