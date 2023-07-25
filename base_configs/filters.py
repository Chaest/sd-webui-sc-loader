c = None

def get_filters(context):
    global c
    c = context
    return {
        'if_tag': lambda v, t: v if t in c.tags else '',
        'build_base_sc': build_base_sc,
        'build_show_sc': build_show_sc
    }

def build_base_sc(general, width, height):
    return {
        'characters': ['char'],
        'prompts': {
            'quality': '$ezpos',
            'general': general,
            'negative': '$ezneg, $not_naked',
            'char': {
                'pre': '',
                'post': ''
            }
        },
        'base_payload': {
            'width': width,
            'height': height
        }
    }

def build_show_sc(general, width, height):
    scenario = build_base_sc(general, width, height)
    if 'portrait' in c.tags:
        scenario['prompts']['general'] += ', portrait, close-up'
    if 'full' in c.tags:
        scenario['prompts']['general'] += ', full body'
    if 'upper' in c.tags:
        scenario['prompts']['general'] += ', upper body, cowboy shot'
    return scenario
