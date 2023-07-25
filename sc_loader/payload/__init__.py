import copy

from .. import context as c
from .coupling import gen_couplings
from .controlnet import update_cn_data
from .ui_inputs_data import apply_ui_inputs
from .prompt import build_prompts

DEFAULT_PAYLOAD_DATA = {
    'steps': 35,
    'cfg_scale': 7.5,
    'width': 512,
    'height': 512,
    'seed_resize_from_h': 0,
    'seed_resize_from_w': 0,
    'restore_faces': False,
    'sampler_name': 'DPM++ 2M Karras',
    'seed': -1,
    'override_settings_restore_afterwards': True
}

def create_payloads():
    skipped_models = []
    for coupling in gen_couplings():
        if coupling[0] in skipped_models:
            print(skipped_models)
            continue
        for payload in create_payloads_for_repeats(*coupling):
            if c.skip_model:
                skipped_models.append(payload['override_settings']['sd_model_checkpoint'])
                c.skip_model = False
            if payload['override_settings']['sd_model_checkpoint'] in skipped_models:
                print('in', skipped_models)
                continue
            yield payload

def create_payloads_for_repeats(model, scenario, *characters):
    for _ in range(c.nb_repeats):
        payload = copy.deepcopy(DEFAULT_PAYLOAD_DATA | scenario['base_payload'])
        update_cn_data(payload)
        apply_ui_inputs(payload, model)
        yield payload | build_prompts(scenario, characters)
