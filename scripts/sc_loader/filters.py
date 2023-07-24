import os

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec

from modules.shared import opts

from . import context as c # pylint: disable=no-name-in-module

def load_filters():
    module = load_filter_module(f'{opts.sc_loader_config_path}/filters.py')
    funcs = getattr(module, 'get_filters', lambda _: {})(c)
    if len(funcs) == 0:
        print('No filters loaded.')
    return funcs

def load_filter_module(path):
    if not os.path.exists(path):
        print('No filters file found.')
        return None

    module_name = 'custom_filters'
    loader = SourceFileLoader(module_name, path)
    spec = spec_from_loader(module_name, loader)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
