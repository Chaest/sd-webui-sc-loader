import os
import zipfile
import requests

DEFAULT_EXPECTED_TYPE = 'Model'
MODEL_TO_EXPECTED_TYPE = {
    'Wildcards': 'Archive',
    'Poses': 'Archive',
    'Other': 'Archive'
}

def model_data(model_id, version):
    print(f'Getting model {model_id}')

    content = requests.get(f'https://civitai.com/api/v1/models/{model_id}', timeout=30).json()

    model = content['modelVersions'][version]
    expected_type = MODEL_TO_EXPECTED_TYPE.get(content['type'], DEFAULT_EXPECTED_TYPE)
    model_file = find_kv('type', expected_type, model['files'])

    if model_file is None:
        raise Exception('Model has no model file that can be downloaded.')

    return content, model, model_file

def download_model(download_url, file_path, type_):
    print(f'Downloading {type_}')

    response = requests.get(download_url, stream=True, timeout=30)
    response.raise_for_status()

    print('Destination:', file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8192):
                fd.write(chunk)
        print(f'{type_.capitalize()} downloaded')
    else:
        print('Model already present')

def download_base_model(download_url, file_path):
    print(f'Downloading base model')

    response = requests.get(download_url, stream=True, timeout=30)
    response.raise_for_status()

    print('Destination:', file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=8192):
                fd.write(chunk)
        print(f'Base model downloaded')
    else:
        print('Model already present')

def download_wildcards(url, folder):
    print('Downloading wildcard')
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    zip_path = os.path.join(os.getcwd(), 'temp.zip')
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    if not os.path.exists(folder):
        os.makedirs(folder)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder)

    os.remove(zip_path)
    print('Wildcard downloaded')

def download_poses(url, folder):
    print('Downloading poses')
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    zip_path = os.path.join(os.getcwd(), 'temp.zip')
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    if not os.path.exists(folder):
        os.makedirs(folder)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder)

    os.remove(zip_path)
    print('Poses downloaded')

def download_package(url, folder):
    print('Downloading package')
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    zip_path = os.path.join(os.getcwd(), 'temp.zip')
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    if not os.path.exists(folder):
        os.makedirs(folder)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder)

    os.remove(zip_path)
    print('Package downloaded')

def find_kv(key, value, list_):
    return (list(filter(lambda e: e[key] == value, list_)) or [None])[0]
