from .. import context as c

def gen_couplings(page=False):
    '''
        The goal of gen_coupling is to generate the multiplicative effect of series
        For the series:
          models: m1, m2
          scenarios: s1, s2
          styles: st1, st2
          char1: c1, c2
          char2: c3, c4

        The couplings will be:
            m1 - s1 - st1 - c1 - c3
            m1 - s1 - st1 - c1 - c4
            m1 - s1 - st1 - c2 - c3
            m1 - s1 - st1 - c2 - c4
            m1 - s1 - st2 - c1 - c3
            m1 - s1 - st2 - c1 - c4
            m1 - s1 - st2 - c2 - c3
            m1 - s1 - st2 - c2 - c4
            m1 - s2 - st1 - c1 - c3
            m1 - s2 - st1 - c1 - c4
            m1 - s2 - st1 - c2 - c3
            m1 - s2 - st1 - c2 - c4
            m1 - s2 - st2 - c1 - c3
            m1 - s2 - st2 - c1 - c4
            m1 - s2 - st2 - c2 - c3
            m1 - s2 - st2 - c2 - c4
            m2 - s1 - st1 - c1 - c3
            m2 - s1 - st1 - c1 - c4
            m2 - s1 - st1 - c2 - c3
            m2 - s1 - st1 - c2 - c4
            m2 - s1 - st2 - c1 - c3
            m2 - s1 - st2 - c1 - c4
            m2 - s1 - st2 - c2 - c3
            m2 - s1 - st2 - c2 - c4
            m2 - s2 - st1 - c1 - c3
            m2 - s2 - st1 - c1 - c4
            m2 - s2 - st1 - c2 - c3
            m2 - s2 - st1 - c2 - c4
            m2 - s2 - st2 - c1 - c3
            m2 - s2 - st2 - c1 - c4
            m2 - s2 - st2 - c2 - c3
            m2 - s2 - st2 - c2 - c4
    '''
    new_lists = []
    series = gen_series(page)
    nb_coupling = get_nb_coupling(series)
    for idx, list_ in enumerate(series):
        len_so_far = len_pn(series, idx)
        growth = int(nb_coupling / len(list_) / len_so_far)
        grown_list = grow(list_, growth)
        new_lists.append(grown_list * len_so_far)
    return list(zip(*new_lists))

def gen_series(page):
    return gen_page_series() if page else gen_scenario_series()

def gen_scenario_series():
    models = c.database['series'].get('models', {}).get(c.model, [c.model])
    scenario_names = c.database['series'].get('scenarios', {}).get(c.scenario, [c.scenario])
    scenarios = [c.database['scenarios'][scenario_name] for scenario_name in scenario_names]
    styles = c.database['prompts'].get('styles', {})
    styles_lists = [
        [styles.get(style_name, '') for style_name in c.database['series'].get('styles', {}).get(style, [style])]
        for style in c.styles
    ]
    characters_lists = [
        c.database['series'].get('characters', {}).get(c.chars[character_idx], [c.chars[character_idx]])
        for character_idx in range(len(scenarios[0]['characters']))
    ]
    return [models, scenarios, *styles_lists, *characters_lists]

def gen_page_series():
    page = c.database['pages'][c.scenario]
    models = c.database['series'].get('models', {}).get(c.model, [c.model])
    styles = c.database['prompts'].get('styles', {})
    styles_lists = [
        [styles.get(style_name, '') for style_name in c.database['series'].get('styles', {}).get(style, [style])]
        for style in c.styles
    ]
    characters_lists = [
        c.database['series'].get('characters', {}).get(c.chars[character_idx], [c.chars[character_idx]])
        for character_idx in range(len(page['characters']))
    ]
    scenarios = [c.database['scenarios'][scenario_name] for scenario_name in page['scenarios']]
    return [models, *styles_lists, *characters_lists, scenarios]

def get_nb_coupling(series):
    list_ = [len(input_list) for input_list in series]
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
