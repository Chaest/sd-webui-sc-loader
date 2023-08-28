from .. import context as c

def update_latent_couple_data(payload):
    if 'alwayson_scripts' not in payload or 'Sc Latent Couple' not in payload['alwayson_scripts']:
        return
    latent_couple_data = payload['alwayson_scripts']['Sc Latent Couple']
    latent_couple_data['args'].append(c.poses_masks_generated)
