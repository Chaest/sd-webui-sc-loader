from . import context as c

def for_tags(options, tags):
    for idx, tag in enumerate(tags):
        if tag in c.tags:
            return options[idx]
    return options[0]

def cn_pose_solo(pose):
    return {
        'controlnet': {'args': [{'input_image': pose, 'model': 'openpose'}]}
    }

def cn_pose(pose, ce_divs, ce_pos, ce_weights):
    return {
        'controlnet': {'args': [{'input_image': pose, 'model': 'openpose'}]},
        'Latent Couple extension': {'args': [True, f'1:1,{ce_divs}', f'0:0,{ce_pos}', f'0.2,{ce_weights}', 150]},
        'Composable Lora': {'args': [True, False, False]}
    }

def cn_pose_for_tags(poses, tags, ce_divs, ce_pos, ce_weights):
    return {
        'controlnet': {'args': [{'input_image': for_tags(poses, tags), 'model': 'openpose'}]},
        'Latent Couple extension': {'args': [True, f'1:1,{ce_divs}', f'0:0,{ce_pos}', f'0.2,{ce_weights}', 150]},
        'Composable Lora': {'args': [True, False, False]}
    }

def grad_desc(lists, tags):
    for i, tag in enumerate(tags[::-1]):
        if tag in c.tags:
            return [
                element
                for list_ in lists[:i+1]
                for element in list_
            ]
    return [
        element
        for list_ in lists
        for element in list_
    ]

def tag_to_db(idx):
    return c.database['prompts'].get(c.tags[idx] if len(c.tags) > idx else '_', '')

FILTERS = {
    'tag_to_db': tag_to_db,
    'tag_nb': lambda n: c.tags[n],
    'for_tags': for_tags,
    'cn_pose': cn_pose,
    'cn_pose_for_tags': cn_pose_for_tags,
    'grad_desc': grad_desc,
    'cn_pose_solo': cn_pose_solo,
    'model_list': lambda l: [{'model': element} for element in l],
    'if_tag': lambda v, t: v if t in c.tags else ''
}