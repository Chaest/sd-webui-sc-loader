from sonotoria import jaml

from modules.shared import opts

from .person import load_people

def openpose_to_scpose(openpose_file):
    openpose_file = openpose_file.replace('.json', '')
    if not openpose_file.startswith(f'{opts.sc_loader_config_path}/poses/'):
        path_to_file = f'{opts.sc_loader_config_path}/poses/{openpose_file}'
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
