from ... import context as c

def apply_fe(payload):
    if not c.fe: return payload
    ao_s = payload.setdefault('alwayson_scripts', {})
    if 'face editor ex' in ao_s: return payload
    ao_s |= {
        'face editor ex': {
            'args': [
                {'save_original_image': True}
            ]
        }
    }
    return payload