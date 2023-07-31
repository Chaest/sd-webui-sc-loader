'''
    This module is mostly made of copied code from a1111 source code that were tweaked to make the developpment easier.
    Everything here should be replaced by less hacky methods and disappear.
'''

import copy

import gradio as gr

from modules import scripts, shared
from modules import processing, ui
from modules.ui import plaintext_to_html
from modules.shared import opts

default_args = None


def txt2img(data):
    global default_args
    script_runner = scripts.scripts_txt2img
    if not script_runner.scripts:
        script_runner.initialize_scripts(False)
        ui.create_ui()
    if not default_args:
        default_args = default_script_args(script_runner)

    args = copy.deepcopy(data)
    args['sampler_index'] = None
    args['do_not_save_samples'] = False
    args['do_not_save_grid'] = True
    args.pop('alwayson_scripts', None)

    script_args = copy.deepcopy(default_args)
    for script_name, script_data in data.get('alwayson_scripts', {}).items():
        alwayson_script = script_runner.scripts[[script.title().lower() for script in script_runner.scripts].index(script_name.lower())]
        for idx in range(0, min((alwayson_script.args_to - alwayson_script.args_from), len(data['alwayson_scripts'][script_name]['args']))):
            script_args[alwayson_script.args_from + idx] = script_data['args'][idx]

    p = processing.StableDiffusionProcessingTxt2Img(sd_model=shared.sd_model, **args)
    p.scripts = script_runner
    p.outpath_grids = opts.outdir_txt2img_grids
    p.outpath_samples = opts.outdir_txt2img_samples

    shared.state.begin()
    p.script_args = tuple(script_args)
    processed = processing.process_images(p)
    shared.state.end()

    return processed.images, processed.js(), plaintext_to_html(processed.info), plaintext_to_html(processed.comments)

def default_script_args(script_runner):
    #find max idx from the scripts in runner and generate a none array to init script_args
    last_arg_index = 1
    for script in script_runner.scripts:
        if last_arg_index < script.args_to:
            last_arg_index = script.args_to
    # None everywhere except position 0 to initialize script args
    script_args = [None]*last_arg_index
    script_args[0] = 0

    # get default values
    with gr.Blocks(): # will throw errors calling ui function without this
        for script in script_runner.scripts:
            if script.ui(False):
                ui_default_values = []
                for elem in script.ui(False):
                    ui_default_values.append(elem.value)
                script_args[script.args_from:script.args_to] = ui_default_values
    return script_args

def selectable_script(script_name, script_runner):
    if script_name is None or script_name == '':
        return None, None

    script_idx = [script.title().lower() for script in script_runner.selectable_scripts].index(script_name.lower())
    script = script_runner.selectable_scripts[script_idx]
    return script, script_idx
