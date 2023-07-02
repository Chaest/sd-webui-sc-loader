import os
import sys
import copy
import threading
import json
from datetime import datetime
import traceback

import gradio as gr

import modules.scripts as scripts
import modules.shared as shared
from modules import script_callbacks, processing, ui, sd_samplers_common, generation_parameters_copypaste
from modules.ui import plaintext_to_html
from modules.ui_common import create_refresh_button
from modules.ui_components import FormRow, FormGroup
from modules.processing import program_version
from modules.shared import opts
from modules.call_queue import wrap_gradio_gpu_call

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)

from sc_loader import context as c
from sc_loader.batch import handle_bob
from sc_loader.config import load_cfg, DB_PATH

TAB_NAME = 'sc_loader'
default_args = None
queue_lock = threading.Lock()
ui_elements = {}
expected_characters_idxs = []
hard_skip_toggled = False


def do_nothing():
    print('HER')

def reload_db():
    c.load_db(opts.sc_loader_config_path)

def create_toprow():
    nb_max_characters = len(c.database['characters'])
    with gr.Row(elem_id=f'{TAB_NAME}_toprow', variant='compact'):
        with gr.Column(elem_id=f'{TAB_NAME}_prompt_container', scale=6):
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Row():
                        def get_bobs():
                            print('HERE')
                            return [f.split('.')[0] for f in os.listdir(opts.sc_loader_config_path+'/bobs')]
                        try:
                            print(bob)
                        except:
                            pass
                        bob = gr.Dropdown(label='Bob', choices=get_bobs(), type='value')
                        print(bob)
                        create_refresh_button(
                            bob,
                            do_nothing,
                            lambda: {'choices': get_bobs()},
                            f'{TAB_NAME}_refresh_bobs'
                        )
                with gr.Column(scale=1):
                    with gr.Row():
                        def get_scenarii():
                            return [f.split('.')[0] for f in os.listdir(opts.sc_loader_config_path+'/scenarii')]
                        scenario = gr.Dropdown(
                            label='Scenario',
                            choices=get_scenarii(),
                            type='value'
                        )
                        create_refresh_button(
                            scenario,
                            do_nothing,
                            lambda: {'choices': get_scenarii()},
                            f'{TAB_NAME}_refresh_scenarii'
                        )
                with gr.Column(scale=1):
                    with gr.Row():
                        tags = gr.Textbox(label='Tags')
                        def get_models():
                            return [model for model in c.database['sd_models']]
                        model = gr.Dropdown(
                            label='Model',
                            choices=get_models(),
                            type='value'
                        )
                        create_refresh_button(
                            model,
                            reload_db,
                            lambda: {'choices': get_models()},
                            f'{TAB_NAME}_refresh_models'
                        )

            with gr.Row():
                with gr.Column(scale=80):
                    characters = [None for _ in range(nb_max_characters)]
                    character_rows = [None for _ in range(nb_max_characters)]
                    for i in range(nb_max_characters):
                        with gr.Row(visible=False) as character_rows[i]:
                            def get_chars():
                                return list(c.database['prompts']['characters'].keys())
                            characters[i] = gr.Dropdown(
                                label=c.database['characters'][i],
                                choices=get_chars(),
                                type='value'
                            )
                            create_refresh_button(
                                characters[i],
                                reload_db,
                                lambda: {'choices': get_chars()},
                                f'{TAB_NAME}_refresh_chars_{i}'
                            )

        with gr.Column(scale=1, elem_id=f'{TAB_NAME}_actions_column'):
            with gr.Row(elem_id=f'{TAB_NAME}_generate_box', elem_classes='generate-box'):
                submit = gr.Button('Generate', elem_id=f'{TAB_NAME}_generate', variant='primary')
                interrupt = gr.Button('Interrupt', elem_id=f'{TAB_NAME}_interrupt')
                skip = gr.Button('Skip', elem_id=f'{TAB_NAME}_skip')
                hard_skip = gr.Button('Hard Skip', elem_id=f'{TAB_NAME}_hard_skip')

                def hard_skipping():
                    global hard_skip_toggled
                    hard_skip_toggled = True
                    shared.state.skip()
                    shared.state.interrupt()

                interrupt.click(fn=shared.state.interrupt)
                skip.click(fn=shared.state.skip)
                hard_skip.click(fn=hard_skipping)

    def switch_sc(scenario):
        global expected_characters_idxs
        data = load_cfg(opts.sc_loader_config_path+'/scenarii/'+scenario+'.yaml')
        expected_characters = data['characters']
        expected_characters_idxs = [c.database['characters'].index(character) for character in expected_characters]
        return [*[
            gr.update(visible=i in expected_characters_idxs)
            for i in range(nb_max_characters)
        ]]
    scenario.change(switch_sc, [scenario], [*character_rows], queue=False)

    return {'bob': bob, 'scenario': scenario, 'tags': tags, 'submit': submit, 'characters': characters, 'model': model}

def sampler_section():
    with FormRow(elem_id=f'sampler_overrides_{TAB_NAME}'):
        override_s = gr.Checkbox(False, label='Override sampler')
        override_ss = gr.Checkbox(False, label='Override sampling steps')
    with FormRow(elem_id=f'sampler_selection_{TAB_NAME}'):
        sampler = gr.Dropdown(
            label='Sampler',
            elem_id=f'{TAB_NAME}_sampling',
            choices=c.database['samplers'],
            type='value'
        )
        steps = gr.Slider(
            minimum=1,
            maximum=150,
            step=1,
            elem_id=f'{TAB_NAME}_steps',
            label='Sampling steps',
            value=20
        )
    return {'sampler': {'override': override_s, 'value': sampler}, 'steps': {'override': override_ss, 'step_value': steps}}

def checkboxes():
    with FormRow(elem_classes='checkboxes-row', variant='compact'):
        restore_faces = gr.Checkbox(
            label='Restore faces',
            value=False,
            elem_id=f'{TAB_NAME}_restore_faces'
        )
        enable_hr = gr.Checkbox(
            label='Hires. fix',
            value=False,
            elem_id=f'{TAB_NAME}_enable_hr'
        )
    return {'rf': restore_faces, 'hr': enable_hr}

def hires_fix():
    with FormGroup(visible=False, elem_id=f'{TAB_NAME}_hires_fix') as hr_options:
        upscaler = gr.Dropdown(
            label='Upscaler',
            elem_id=f'{TAB_NAME}_hr_upscaler',
            choices=c.database['upscalers'],
            type='value'
        )
        scale = gr.Slider(
            minimum=1.0,
            maximum=4.0,
            step=0.05,
            label='Upscale by',
            value=2.5,
            elem_id=f'{TAB_NAME}_hr_scale'
        )
        strength = gr.Slider(
            minimum=0.0,
            maximum=1.0,
            step=0.01,
            label='Denoising strength',
            value=0.37,
            elem_id=f'{TAB_NAME}_denoising_strength'
        )

    return {'upscaler': upscaler, 'scale': scale, 'strength': strength, 'hr_options': hr_options}

def cfg_scale():
    with FormRow(elem_id=f'cfg_overrides_{TAB_NAME}'):
        use_clip_skip = gr.Checkbox(False, label='Use clip skip')
        use_scale = gr.Checkbox(False, label='Use scale')
    with FormRow(elem_id=f'sampler_selection_{TAB_NAME}'):
        clip_skip = gr.Number(label='Clip skip', value=opts.CLIP_stop_at_last_layers, elem_id=f'{TAB_NAME}_clip_skip')
        scale = gr.Slider(
            minimum=0.0,
            maximum=30.0,
            step=0.5,
            label='Cfg scale',
            value=7.0,
            elem_id=f'{TAB_NAME}_cfg_scale'
        )

    return {'use_scale': use_scale, 'cfg_scale': scale, 'use_clip_skip': use_clip_skip, 'clip_skip': clip_skip}

def seed_picker():
    with FormRow(elem_id=f'{TAB_NAME}_seed_row', variant='compact'):
        seed = gr.Number(label='Seed', value=-1, elem_id=f'{TAB_NAME}_seed')
        seed.style(container=False)
    return {'seed': seed}

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

def create_output_panel(outdir):
    def open_folder(f):
        if not shared.cmd_opts.hide_ui_dir_config:
            path = os.path.normpath(f)
            os.startfile(path)

    with gr.Column(variant='panel', elem_id=f'{TAB_NAME}_results'):
        with gr.Group(elem_id=f'{TAB_NAME}_gallery_container'):
            result_gallery = gr.Gallery(label='Output', show_label=False, elem_id=f'{TAB_NAME}_gallery').style(columns=4)

        generation_info = None
        with gr.Column():
            with gr.Row(elem_id=f'image_buttons_{TAB_NAME}', elem_classes='image-buttons'):
                open_folder_button = gr.Button('\U0001f4c2')
            open_folder_button.click(
                fn=lambda: open_folder(outdir),
                inputs=[],
                outputs=[],
            )

            with gr.Group():
                html_info = gr.HTML(elem_id=f'html_info_{TAB_NAME}', elem_classes='infotext')
                html_log = gr.HTML(elem_id=f'html_log_{TAB_NAME}')

                generation_info = gr.Textbox(visible=False, elem_id=f'generation_info_{TAB_NAME}')

            return result_gallery, generation_info, html_info, html_log

def create_infotext(p, all_prompts, all_seeds, all_subseeds, comments=None, iteration=0, position_in_batch=0):
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

def bobing(_bob, bob, scenario, tags, upscaler, hr, rf, use_scale, cfg_scale, model, use_clip_skip, clip_skip, *characters):
    global ui_elements, expected_characters_idxs, hard_skip_toggled

    c.init(opts.sc_loader_config_path)
    c.tags = tags.split(',')
    c.model = model
    c.hr = hr
    c.restore = rf
    c.upscaler = upscaler or c.upscaler
    c.scenario = scenario
    c.cfg_scale = cfg_scale if use_scale else None
    c.chars = [characters[idx] for idx in expected_characters_idxs]

    print(opts.sc_loader_config_path, c.tags, c.hr, c.restore, c.upscaler, c.scenario, c.chars, bob, _bob)

    if use_clip_skip:
        old_clip_skip_value = opts.CLIP_stop_at_last_layers
        opts.CLIP_stop_at_last_layers = int(clip_skip)

    true_create_infotext = processing.create_infotext
    processing.create_infotext = create_infotext

    gallery = []
    first_gen = None
    try:
        for payload in handle_bob(bob, opts.sc_loader_config_path):
            if hard_skip_toggled:
                hard_skip_toggled = False
                break

            txt2img_gallery, generation_info, html_info, html_log = txt2img(payload)
            first_gen = first_gen or generation_info
            gallery += txt2img_gallery


            date = datetime.today().strftime('%Y-%m-%d')
            samples_dir = opts.outdir_txt2img_samples + '/' + date
            last_file_name = sorted([f for f in os.listdir(samples_dir)])[-1].split('.')[0]

            with open(f'{samples_dir}/{last_file_name}a - {c.c["model"]}.json', 'w') as fp:
                payload['date'] = date
                json.dump(payload, fp, indent=4)
    except:
        print(traceback.format_exc())

    processing.create_infotext = true_create_infotext

    if use_clip_skip:
        opts.CLIP_stop_at_last_layers = old_clip_skip_value

    try:
        return gallery, generation_info, html_info, html_log
    except:
        return gallery, first_gen or '{}', plaintext_to_html(''), plaintext_to_html('')


def create_ui():
    global ui_elements

    c.init(opts.sc_loader_config_path)

    with gr.Blocks(analytics_enabled=False) as ui_component:
        ui_elements = create_toprow()

        with gr.Row().style(equal_height=False):
            with gr.Column(variant='compact', elem_id=f'{TAB_NAME}_settings'):
                ui_elements |= checkboxes()
                ui_elements |= hires_fix()
                ui_elements |= cfg_scale()
                ui_elements |= sampler_section()
                ui_elements |= seed_picker()

            txt2img_gallery, generation_info, html_info, html_log = create_output_panel(opts.outdir_txt2img_samples)

            ui_elements['submit'].click(
                fn=wrap_gradio_gpu_call(bobing, extra_outputs=[None, '', '']),
                _js='submit_sc_loader',
                inputs=[
                    ui_elements['bob'],
                    ui_elements['bob'],
                    ui_elements['scenario'],
                    ui_elements['tags'],
                    ui_elements['upscaler'],
                    ui_elements['hr'],
                    ui_elements['rf'],
                    ui_elements['use_scale'],
                    ui_elements['cfg_scale'],
                    ui_elements['model'],
                    ui_elements['use_clip_skip'],
                    ui_elements['clip_skip'],
                    *ui_elements['characters']
                ],
                outputs=[txt2img_gallery, generation_info, html_info, html_log],
                show_progress=False
            )

            ui_elements['hr'].change(
                fn=lambda x: gr.update(visible=x),
                inputs=[ui_elements['hr']],
                outputs=[ui_elements['hr_options']],
                queue=False
            )

        return [(ui_component, 'Sc Loader', 'sc_loader')]

def create_ui_settings():
    section = ('sc_loader', 'Scenario loader')
    shared.opts.add_option(
        'sc_loader_config_path',
        shared.OptionInfo(
            'extensions/sd-webui-sc-loader/base_configs',
            'Path to configuration',
            gr.Textbox,
            {'interactive': True},
            section=section
        )
    )

script_callbacks.on_ui_settings(create_ui_settings)
script_callbacks.on_ui_tabs(create_ui)