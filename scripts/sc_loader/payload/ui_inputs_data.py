from .. import context as c

def apply_ui_inputs(payload, model):
    payload['override_settings'] = {'sd_model_checkpoint': model}
    payload['batch_size'] = c.nb_iter
    payload['n_iter'] = c.nb_batches
    if c.sampler:
        payload['sampler_name'] = c.sampler
    if c.steps:
        payload['steps'] = c.steps
    if c.cfg_scale:
        payload['cfg_scale'] = c.cfg_scale
    if c.restore:
        payload['restore_faces'] = True
    if c.hr:
        payload['enable_hr'] = True
        payload['denoising_strength'] = c.denoising_strength or 0.37
        payload['hr_scale'] = c.upscale_by or 2.5
        payload['hr_upscaler'] = c.upscaler or 'R-ESRGAN 4x+'
        payload['batch_size'] = 3
        w = payload['width']
        h = payload['height']
        if w > 512 or h > 512:
            mx = max(w, h)
            ratio = float(512)/float(mx)
            payload['width'] = int(float(payload['width']) * ratio)
            payload['height'] = int(float(payload['height']) * ratio)
