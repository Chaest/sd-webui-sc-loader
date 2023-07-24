'''
    This module is mostly made of copied code from a1111 source code that were tweaked to make the developpment easier.
    Everything here should be replaced by less hacky methods and disappear.
'''

import copy

import gradio as gr

from modules import scripts, shared
from modules import processing, ui, sd_samplers_common, generation_parameters_copypaste
from modules.ui import plaintext_to_html
from modules.processing import program_version
from modules.shared import opts

from .. import context as c

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

def create_infotext(p, all_prompts, all_seeds, all_subseeds, comments=None, iteration=0, position_in_batch=0): # pylint: disable=too-many-arguments,unused-argument
    ### Unaltered code from the function found in processing

    index = position_in_batch + iteration * p.batch_size

    clip_skip = getattr(p, 'clip_skip', opts.CLIP_stop_at_last_layers)
    enable_hr = getattr(p, 'enable_hr', False)
    token_merging_ratio = p.get_token_merging_ratio()
    token_merging_ratio_hr = p.get_token_merging_ratio(for_hr=True)

    uses_ensd = opts.eta_noise_seed_delta != 0
    if uses_ensd:
        uses_ensd = sd_samplers_common.is_sampler_using_eta_noise_seed_delta(p)

    generation_params = {
        "Steps": p.steps,
        "Sampler": p.sampler_name,
        "CFG scale": p.cfg_scale,
        "Image CFG scale": getattr(p, 'image_cfg_scale', None),
        "Seed": all_seeds[index],
        "Face restoration": (opts.face_restoration_model if p.restore_faces else None),
        "Size": f"{p.width}x{p.height}",
        "Model hash": getattr(p, 'sd_model_hash', None if not opts.add_model_hash_to_info or not shared.sd_model.sd_model_hash else shared.sd_model.sd_model_hash),
        "Model": (None if not opts.add_model_name_to_info or not shared.sd_model.sd_checkpoint_info.model_name else shared.sd_model.sd_checkpoint_info.model_name.replace(',', '').replace(':', '')),
        "Variation seed": (None if p.subseed_strength == 0 else all_subseeds[index]),
        "Variation seed strength": (None if p.subseed_strength == 0 else p.subseed_strength),
        "Seed resize from": (None if p.seed_resize_from_w == 0 or p.seed_resize_from_h == 0 else f"{p.seed_resize_from_w}x{p.seed_resize_from_h}"),
        "Denoising strength": getattr(p, 'denoising_strength', None),
        "Conditional mask weight": getattr(p, "inpainting_mask_weight", shared.opts.inpainting_mask_weight) if p.is_using_inpainting_conditioning else None,
        "Clip skip": None if clip_skip <= 1 else clip_skip,
        "ENSD": opts.eta_noise_seed_delta if uses_ensd else None,
        "Token merging ratio": None if token_merging_ratio == 0 else token_merging_ratio,
        "Token merging ratio hr": None if not enable_hr or token_merging_ratio_hr == 0 else token_merging_ratio_hr,
        "Init image hash": getattr(p, 'init_img_hash', None),
        "RNG": opts.randn_source if opts.randn_source != "GPU" else None,
        "NGMS": None if p.s_min_uncond == 0 else p.s_min_uncond,
        **p.extra_generation_params,
        "Version": program_version() if opts.add_version_to_infotext else None,
    }

    generation_params_text = ", ".join([k if k == v else f'{k}: {generation_parameters_copypaste.quote(v)}' for k, v in generation_params.items() if v is not None])

    ### Changes start here

    return f'{c.short_prompts["positive"]}\nNegative prompt: {c.short_prompts["negative"]}\n{generation_params_text}'.strip()

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
