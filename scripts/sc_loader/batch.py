from .payload import create_payload
from .config import load_cfg
from .tags import update_tags
from . import context as c

DEFAULT_BATCH_DATA = {
    'sampler_name': 'm_karras',
    'batch_size': 4,
    'n_iter': 1,
    'restore_faces': False,
    'seed': -1
}

def handle_bob(bob, current_dir):
    bob = load_cfg(current_dir + '/bobs/' + bob)
    c.scenario = c.scenario or bob.get('default_scenario')
    update_tags(bob.get('tags', []))

    if isinstance(bob['batches'], list):
        for payload in handle_batch_list(bob, bob['batches'], current_dir):
            yield payload

    if isinstance(bob['batches'], dict):
        common_tags = list(c.tags)
        for _, batch_group in bob['batches'].items():
            c.tags = list(common_tags)
            update_tags(batch_group.get('tags', []))
            for payload in handle_batch_list(bob, batch_group['batches'], current_dir):
                yield payload

def handle_batch_list(bob, batches, current_dir):
    for batch in batches:
        c.scenario = batch.get('scenario', c.scenario)

        for dflt in ('batch_size', 'n_iter', 'repeat'):
            if dflt in bob and dflt not in batch:
                batch[dflt] = bob[dflt]

        for k, v in batch.items():
            print(k, '=', v)

        for _ in range(batch.get('repeat', 1)):
            batch_data = {k: v for k, v in batch.items() if k not in ('repeat', 'scenario', 'inputs')}
            yield handle_batch(batch_data, current_dir)

def handle_batch(batch, current_dir):
    c.sc_data = load_cfg(current_dir + '/scenarii/' + c.scenario)

    update_batch(batch)
    update_tags(batch.get('tags', []))
    update_batch_data()

    return create_payload(current_dir)

def update_batch(batch):
    if batch is None:
        return c.sc_data['default_batch']
    if isinstance(batch, str):
        return load_cfg(batch)
    c.batch = batch

def update_batch_data():
    c.batch_data = dict(DEFAULT_BATCH_DATA | c.batch)
    c.batch_data['sampler_name'] = c.database['samplers'][c.batch_data['sampler_name']]
    c.batch_data['override_settings'] = {'sd_model_checkpoint': c.database['sd_models'][c.batch_data.get('model', c.model)]}
    c.batch_data['override_settings_restore_afterwards'] = True
    c.c['model'] = c.batch_data.get('model', c.model)
    if 'model' in c.batch_data:
        del c.batch_data['model']
