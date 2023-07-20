from .payload import create_payloads
from . import context as c

def prod(list_):
    start = 1
    for element in list_:
        start *= element
    return start

def len_pn(lol, idx):
    result = 1
    for list_ in lol[:idx]:
        result *= len(list_)
    return result

def grow(list_, size):
    return [
        element
        for element in list_
        for _ in range(size)
    ]

def gen_couplings(lol, full_length):
    nlol = []
    for idx, list_ in enumerate(lol):
        len_so_far = len_pn(lol, idx)
        growth = int(full_length / len(list_) / len_so_far)
        grown_list = grow(list_, growth)
        nlol.append(grown_list * len_so_far)
    return nlol

def payloads():
    models = c.database['series'].get('models', {}).get(c.model, [c.model])
    scenario_names = c.database['series'].get('scenarios', {}).get(c.scenario, [c.scenario])
    scenarios = [c.database['scenarios'][scenario_name] for scenario_name in scenario_names]
    characters_lists = [
        c.database['series'].get('characters', {}).get(c.chars[character_idx], [c.chars[character_idx]])
        for character_idx in range(len(scenarios[0]['characters']))
    ]
    input_lists = [models, scenarios, *characters_lists]
    full_length = prod(len(input_list) for input_list in input_lists)
    input_couplings = list(zip(*gen_couplings(input_lists, full_length)))
    skipped_models = []
    for input_coupling in input_couplings:
        if input_coupling[0] in skipped_models:
            print(skipped_models)
            continue
        for payload in create_payloads(*input_coupling):
            if c.skip_model:
                skipped_models.append(payload['override_settings']['sd_model_checkpoint'])
                c.skip_model = False
            if payload['override_settings']['sd_model_checkpoint'] in skipped_models:
                print('in', skipped_models)
                continue
            yield payload
