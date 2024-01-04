from ... import context as c

def apply_ad(payload):
    if not c.ad: return payload
    ao_s = payload.setdefault('alwayson_scripts', {})
    if 'ADetailer' in ao_s: return payload
    ao_s |= {
        'ADetailer': {
            'args': [
                {'ad_model': 'person_yolov8s-seg.pt'},
                {'ad_model': 'face_yolov8n.pt'}
            ]
        }
    }
    return payload