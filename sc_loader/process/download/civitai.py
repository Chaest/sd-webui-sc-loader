import os
import zipfile
import requests
import traceback
import hashlib

from modules.shared import opts

from sc_loader.process.sd import basemodels_dir, lora_dir, lyco_dir, embeddings_dir

from .handlers import batch
from .db import get_wildcard_path, get_poses_path, get_package_path

DDL_RETRIES = 5
ZIP_PATH = os.path.join(os.getcwd(), 'temp.zip')
DEFAULT_EXPECTED_TYPE = 'Model'
MODEL_TO_EXPECTED_TYPE = {
    'Wildcards': 'Archive',
    'Poses': 'Archive',
    'Other': 'Archive'
}
TYPE_TO_PATH = {
    'wildcard': get_wildcard_path,
    'Poses': get_poses_path,
    'Package': get_package_path
}
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

class CivitAIModel:
    def __init__(self, model_id, version=0):
        self.id = model_id
        self.version = version
        self.gather_data()

    def gather_data(self):
        print('Gathering model data for id:', self.id)
        remaining_tries = 4
        while True:
            try:
                self.data = requests.get(f'https://civitai.com/api/v1/models/{self.id}', timeout=30).json()
                break
            except Exception as e:
                remaining_tries -= 1
                print(e)
                print(f'Remaining tries: {remaining_tries}')
                if remaining_tries > 0:
                    print('Retrying...')
                else:
                    raise Exception('Could not gather model data') from e

        self.model = self.data['modelVersions'][self.version]
        self.expected_type = MODEL_TO_EXPECTED_TYPE.get(self.data['type'], DEFAULT_EXPECTED_TYPE)
        self.model_file = find_kv('type', self.expected_type, self.model['files'])
        self.type = TYPE_MAPPER[self.data['type']]
        self.full_hash = self.model_file['hashes'].get('SHA256')
        self.small_hash = self.model_file['hashes'].get('AutoV2', self.data['creator'].get('username', 'undefined'))
        self.download_url = self.model_file['downloadUrl']
        self.file_name_wo_ext, self.file_name = specific_name(self.model_file['name'], self.small_hash)
        self.file_path = os.path.join(TYPE_TO_FOLDER[self.type], self.file_name)
        self.trained_words = self.model.get('trainedWords', [])
        self.name = self.data['name']

        if self.model_file is None:
            raise Exception('Model has no model file that can be downloaded.')

        print('Model data successfully gathered.')

    def prompt(self, weight):
        if self.type == 'ti':
            if weight == 1:
                return self.file_name_wo_ext
            if weight == 1.1: # for the sake of beauty
                return f'({self.file_name_wo_ext})'
            if weight == 1.2: # for the sake of beauty
                return f'(({self.file_name_wo_ext}))'
            return f'({self.file_name_wo_ext}:{weight})'
        if self.type in ('lora', 'lyco'):
            return f'<{self.type}:{self.file_name_wo_ext}:{weight}>'
        return ''

    def should_download(self, path):
        if not os.path.exists(path): return True
        with open(path, 'rb') as f:
            fbytes = f.read()
        hash_method = hashlib.sha256()
        hash_method.update(fbytes)
        if self.full_hash != hash_method.hexdigest().upper():
            print(f'Hash mismatch:\n  Expected: {self.full_hash}\n  Found: {hash_method.hexdigest().upper()}')
            return True

    def download(self, update=False):
        if self.expected_type == 'Archive':
            return self._download_archive(update)
        return self._download_model()

    def try_and_download(self, path):
        remaining_tries = DDL_RETRIES
        while self.should_download(path):
            if remaining_tries != DDL_RETRIES:
                print(f'Retry (remaining: {remaining_tries})')
            headers = {} if not opts.sc_loader_civitai_api_key else {'Authorization': f'Bearer {opts.sc_loader_civitai_api_key}'}
            response = requests.get(self.download_url, stream=True, timeout=20000, headers=headers)
            response.raise_for_status()
            with open(path, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    fd.write(chunk)

            if remaining_tries > 0:
                remaining_tries -= 1
            else:
                os.remove(path)
                raise Exception(f'{self.type.capitalize()} failed to download')

        return remaining_tries

    def _download_model(self):
        print('Downloading', self.type)
        print('Destination:', self.file_path)

        remaining_tries = self.try_and_download(self.file_path)

        print(self.type.capitalize(), 'already present' if remaining_tries == DDL_RETRIES else 'successfully downloaded')

    def _download_archive(self, update):
        print('Downloading', self.type)

        self.try_and_download(ZIP_PATH)

        folder = TYPE_TO_PATH[self.type](self.name)
        exists = True
        if not os.path.exists(folder):
            os.makedirs(folder)
            exists = False

        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            if update or not exists:
                zip_ref.extractall(folder)

        os.remove(ZIP_PATH)

        if self.type == 'Package':
            self.pkg_results = ''
            if os.path.exists(f'{folder}/batches'):
                for file_ in os.listdir(f'{folder}/batches'):
                    if file_.endswith('.txt'):
                        try:
                            self.pkg_results += f'<br>Results for {file_}:<br>'
                            self.pkg_results += batch.process_batch(f'{folder}/batches/{file_}')
                        except:
                            print(f'Batch {file_} failed')
                            print(traceback.format_exc())
            return self.pkg_results


def specific_name(filename, hash_):
    base_name, ext = os.path.splitext(filename)
    hashed_name = f'{base_name}_{hash_}'
    return hashed_name, f'{hashed_name}{ext}'

def find_kv(key, value, list_):
    return (list(filter(lambda e: e[key] == value, list_)) or [None])[0]
