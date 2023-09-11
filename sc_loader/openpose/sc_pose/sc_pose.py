from sonotoria import jaml

from .person import load_people
from ...context import get_cfg_path

def openpose_to_scpose(openpose_file):
    openpose_file = openpose_file.replace('.json', '')
    if not openpose_file.startswith(f'{get_cfg_path()}/poses/'):
        path_to_file = f'{get_cfg_path()}/poses/{openpose_file}'
    else:
        path_to_file = openpose_file
    openpose = jaml.load(path_to_file+'.json')
    jaml.dump(
        path_to_file+'.yaml',
        {
            'canvas': {
                'width': openpose['canvas_width'],
                'height': openpose['canvas_height']
            },
            'people': load_people(openpose)
        }
    )
    return f'Openpose [{openpose_file}.json] successfully transformed to ScPose [{openpose_file}.yaml]!'
