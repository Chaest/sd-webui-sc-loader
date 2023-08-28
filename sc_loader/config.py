import os
import copy

from sonotoria import jaml

from .filters import load_filters

def load_yaml_dict(path):
    value = jaml.load(path, filters=load_filters())
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return {path_to_name(path): value}
    print(f'[ERROR] Expected dict or list at {path}, value ignored...')
    return {}

def load_file_as_str(path):
    try:
        with open(path, 'r', encoding='utf-8') as file_:
            return file_.read()
    except:
        print(f'[ERROR] Could not read {path}')
        return ''

def load_txt_list(path):
    return load_file_as_str(path).strip().replace('\r', '').split('\n')

def path_to_name(path):
    return path.split('/')[-1].split('.')[0]

def load_dir_element(path):
    data = {}
    for path_ in os.listdir(path):
        path_ = path + '/' + path_
        if os.path.isdir(path_):
            data = merged_dicts(data, load_dir_element(path_))
        else:
            data = merged_dicts(data, load_file_element(path_))
    return data if path.split('/')[-1][0] == '_' else {path_to_name(path): data}

def load_file_element(path):
    if not os.path.exists(path):
        print(f'[ERROR] {path} not found, ignored...')
        return {}

    if path.endswith(('.json', '.yml', '.yaml')):
        data = load_yaml_dict(path)
        if isinstance(data, dict):
            return data

    elif path.endswith(('.text', '.txt')):
        data = load_txt_list(path)

    else:
        data = load_file_as_str(path)

    return {path_to_name(path): data}

def merged_dicts(d1, *dicts):
    res = copy.deepcopy(d1 or {})
    for d2 in dicts:
        rec_add_dict(res, d2 or {}, [])
    return res

def rec_add_dict(dest, src, path):
    for k, v in src.items():
        if k not in dest:
            dest[k] = copy.deepcopy(v)
        else:
            type_match =(type(dest[k]), type(v))
            if type_match == (list, list):
                dest[k] += v
            elif type_match == (dict, dict):
                rec_add_dict(dest[k], v, path + [k])
            else:
                raise Exception(f'Trying to replace existing value for key {k} at {" -> ".join(path)}.')

def load_cfg(cfg_path):
    if not cfg_path.endswith('.yaml'):
        cfg_path = cfg_path + '.yaml'
    cfg = jaml.load(cfg_path, filters=load_filters())
    return cfg
