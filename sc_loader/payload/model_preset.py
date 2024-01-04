from .. import context as c

PRESET2PAYLOAD = {
    'cfg_scale': 'cfg_scale',
    'strength': 'denoising_strength',
    'steps': 'steps',
    'upscaler': 'hr_upscaler',
    'upscale_scale': 'hr_scale',
    'sampler': 'sampler_name',
    'positive': 'prompt',
    'negative': 'negative_prompt'
}
OPTIONALS = ('cfg_scale', 'strength', 'steps', 'upscaler', 'sampler')
PREPENDERS = ('positive', 'negative')

def apply_model_preset(payload, model):
    if not c.enable_models_presets: return

    preset = c.database.get('model_presets', {}).get(model)
    print(model, preset)
    if not preset:
        return

    for optional in OPTIONALS:
        if optional in preset:
            payload[PRESET2PAYLOAD[optional]] = preset[optional]

    for prepender in PREPENDERS:
        payload[PRESET2PAYLOAD[prepender]] = preset[prepender] + ', ' + payload[PRESET2PAYLOAD[prepender]]
