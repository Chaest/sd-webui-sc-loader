from .. import context as c

def apply_ui_inputs(payload, model):
    payload['override_settings'] = {'sd_model_checkpoint': model}
    if c.use_clip_skip:
        payload['override_settings']['CLIP_stop_at_last_layers'] = c.clip_skip
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
        w = payload['width']
        h = payload['height']
