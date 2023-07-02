from contextlib import contextmanager
import json

from sonotoria import jaml

from .filters import FILTERS
from .tags import update_tags

DB_PATH = 'db.yaml'
SC_DB_PATH = 'db.json'

def load_cfg(cfg_path):
    if not cfg_path.endswith('.yaml'):
        cfg_path = cfg_path + '.yaml'
    cfg = jaml.load(cfg_path, filters=FILTERS)
    update_tags(cfg.get('tags', []))
    return cfg

def load_sc_db(db_path):
    try:
        with open(db_path, 'r') as fp:
            return json.load(fp)
    except:
        return {}

def update_sc_db(db_path, db):
    with open(db_path, 'w') as fp:
        json.dump(db, fp)

@contextmanager
def sc_db(sc_path):
    db_path = f'{sc_path}/{SC_DB_PATH}'
    db = load_sc_db(db_path)
    yield db
    update_sc_db(db_path, db)