import copy

from .. import context as c
from .coupling import gen_couplings
from .controlnet import update_cn_data
from .latent_couple import update_latent_couple_data
from .ui_inputs_data import apply_ui_inputs
from .model_preset import apply_model_preset
from .prompt import build_prompts

MODEL_IDX = 0
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
        if coupling[MODEL_IDX] in skipped_models:
            continue
        for payload in create_payloads_for_repeats(*coupling):
            c.current_payload = payload
            if c.skip_model:
                skipped_models.append(c.skipped_model)
                c.skip_model = False
            if payload['override_settings']['sd_model_checkpoint'] in skipped_models:
                continue
            yield payload
    c.current_payload = None

def create_payloads_for_page():
    skipped_models = []
    page = c.database['pages'][c.scenario]
    nb_scenarios = len(page['scenarios'])
    coupling_idx = 0
    couplings = gen_couplings(True)
    while coupling_idx != len(couplings):
        for _ in range(c.nb_repeats):
            for coupling in couplings[coupling_idx:coupling_idx+nb_scenarios]:
                if coupling[MODEL_IDX] in skipped_models:
                    continue
                scenario = coupling[-1]
                char_to_idx = {v: i for i, v in enumerate(page['characters'])}
                # coupling is models - (styles) - (characters) - scenario
                # thus characters start a 1 + len(styles)
                characters = [
                    coupling[char_to_idx[character]+1+len(c.styles)]
                    for character in scenario['characters']
                ]
                payload = create_payload(coupling[0], scenario, *coupling[1:len(c.styles)+1], *characters)
                c.current_payload = payload
                if c.skip_model:
                    skipped_models.append(c.skipped_model)
                    c.skip_model = False
                if payload['override_settings']['sd_model_checkpoint'] in skipped_models:
                    continue
                yield payload
            yield None
        coupling_idx += nb_scenarios
    c.current_payload = None

def create_payloads_for_repeats(model, scenario, *styles_and_characters):
    for _ in range(c.nb_repeats):
        yield create_payload(model, scenario, *styles_and_characters)

def create_payload(model, scenario, *styles_and_characters):
    payload = copy.deepcopy(DEFAULT_PAYLOAD_DATA | scenario['base_payload'])
    update_cn_data(payload)
    update_latent_couple_data(payload)
    apply_ui_inputs(payload, model)
    styles = styles_and_characters[:len(c.styles)]
    characters = styles_and_characters[len(c.styles):]
    payload |= build_prompts(scenario, styles, characters)
    apply_model_preset(payload, model)
    return payload
