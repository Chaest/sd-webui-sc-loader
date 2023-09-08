from sc_loader.openpose.json_to_openpose import from_json
from sc_loader.openpose.sc_pose.convert import from_sc_pose

from .params import params_to_filters
from ... import context as c

def do_visualize(divisions, positions, weights, pose):
    if not pose:
        pose = None
    else:
        payload = {'alwayson_scripts': {'Sc Latent Couple': {'args':  [True, divisions, positions, weights]}}}
        if pose.endswith('.json'):
            from_json(pose, payload)
        else:
            from_sc_pose(pose, payload)
        pose = c.poses_masks_generated
    return [
        f.create_tensor(1, 128, 128).squeeze(dim=0).cpu().numpy()
        for f in params_to_filters(divisions, positions, weights, pose)
    ]

def denoised_callback(params):
    enabled, masks, num_batches, end_at_step = c.denoise_args

    if not enabled: return

    if params.sampling_step < end_at_step:
        x = params.x # x.shape = [batch_size, C, H // 8, W // 8]
        num_prompts = x.shape[0] // num_batches
        filters = [
            f.create_tensor(x.shape[1], x.shape[2], x.shape[3])
            for f in masks
        ]
        neg_filters = [1.0 - f for f in filters]

        tensor_off = 0
        uncond_off = num_batches * num_prompts - num_batches
        for b in range(num_batches):
            uncond = x[uncond_off, :, :, :]

            for p in range(num_prompts - 1):
                if p < len(filters):
                    tensor = x[tensor_off, :, :, :]
                    x[tensor_off, :, :, :] = tensor * filters[p] + uncond * neg_filters[p]

                tensor_off += 1

            uncond_off += 1
