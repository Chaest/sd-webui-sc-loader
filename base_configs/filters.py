c = None

def get_filters(context):
    global c
    c = context
    return {
        'build_base_sc': build_base_sc
    }

def build_base_sc(general, width, height):
    return {
        'characters': ['character1'],
        'prompts': {
            'quality': '$positive',
            'general': general,
            'negative': '$negative',
            'character1': {
                'pre': '',
                'post': ''
            }
        },
        'base_payload': {
            'width': width,
            'height': height
        }
    }
