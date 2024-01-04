'''
    This module is mostly made of copied code from a1111 source code that were tweaked to make the developpment easier.
    Everything here should be replaced by less hacky methods and disappear.

    Also, concerning mov2mov:
        Code taken and adapted from https://github.com/Scholar01/sd-webui-mov2mov/tree/master
        In accordance to https://github.com/Scholar01/sd-webui-mov2mov/blob/master/LICENSE
        For simplification
'''

import copy
import os
import base64

import cv2
import requests
from io import BytesIO
from PIL import Image
import gradio as gr

from modules import scripts, shared
from modules import processing, ui
from modules.ui import plaintext_to_html
from modules.shared import opts
from modules.processing import Processed

from sc_loader import context as c
from sc_loader.process.m2m import process_mov2mov, scripts_mov2mov

default_args = None

EXPECTED_KEYS = 'prompt', 'negative_prompt', 'steps', 'sampler_name', 'cfg_scale', 'denoising_strength', 'override_settings'
DEFAULT_VALUES = {
    'styles': [],
    'batch_size': 1,
    'n_iter': 1,
    'init_images': [None],
    'mask': None,
    'inpainting_fill': 1,
    'resize_mode': 0,
    'image_cfg_scale': 1.5,
    'inpaint_full_res': False,
    'inpaint_full_res_padding': 32,
    'inpainting_mask_invert': 0,
    'initial_noise_multiplier': 1
}


def data2img(data):
    if 'img' in data:
        imgs = adapt4img(data)
        return img2img(imgs, data)
    if 'mov' in data:
        return mov2mov(data)
    return txt2img(data)

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


def img2img(imgs, data):
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

    p = processing.StableDiffusionProcessingImg2Img(sd_model=shared.sd_model, **args)
    p.init_images = [
        Image.open(BytesIO(requests.get(img).content) if img.startswith('http') else f'{c.get_cfg_path()}/{img}')
        for img in imgs
    ]
    p.scripts = script_runner
    p.outpath_grids = opts.outdir_txt2img_grids
    p.outpath_samples = opts.outdir_txt2img_samples

    shared.state.begin()
    p.script_args = tuple(script_args)
    processed = processing.process_images(p)
    shared.state.end()

    return processed.images, processed.js(), plaintext_to_html(processed.info), plaintext_to_html(processed.comments)

def mov2mov(data):

    args = copy.deepcopy(data)
    args['sampler_index'] = None
    args['do_not_save_samples'] = False
    args['do_not_save_grid'] = True
    args.pop('alwayson_scripts', None)

    mask_blur = 4
    mov_path = f'{c.get_cfg_path()}/{data["mov"]}'
    mov_data = get_mov_data(mov_path)
    p = processing.StableDiffusionProcessingImg2Img(
        sd_model=shared.sd_model,
        outpath_samples=opts.outdir_txt2img_samples,
        outpath_grids=opts.outdir_txt2img_grids,
        **DEFAULT_VALUES,
        **{k: data[k] for k in EXPECTED_KEYS},
        width=mov_data['width'],
        height=mov_data['height'],
        mask_blur=mask_blur,
    )
    p.scripts = scripts_mov2mov
    p.script_args = args
    p.extra_generation_params['Mask blur'] = mask_blur

    generate_video = process_mov2mov(p, mov_path, mov_data['nb_frame'], -1, 0, mov_data['width'], mov_data['height'], args)
    processed = Processed(p, [], p.seed, "")

    p.close()
    shared.total_tqdm.clear()

    return generate_video, processed.js(), plaintext_to_html(processed.info), plaintext_to_html(processed.comments, classname='comments')

def get_mov_data(mov_path):
    if mov_path.endswith('.mp4'):
        cap = cv2.VideoCapture(mov_path)
        data = {
            'width': cap.get(cv2.CAP_PROP_FRAME_WIDTH),
            'height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'nb_frame': cap.get(cv2.CAP_PROP_FRAME_COUNT)
        }
        cap.release()
    else:
        gif = Image.open(mov_path)
        width, height = gif.size
        frame_count = 0
        while True:
            try:
                gif.seek(frame_count)
                frame_count += 1
            except EOFError:
                break
        data = {
            'width': width,
            'height': height,
            'nb_frame': frame_count
        }
    return data

def adapt4img(data):
    imgs = data['img'] if isinstance(data['img'], list) else [data['img']]
    data['init_images'] = [
        Image.open(BytesIO(requests.get(img).content) if img.startswith('http') else f'{c.get_cfg_path()}/{img}')
        for img in imgs
    ]
    del data['img']
    if 'enable_hr' in data:
        data['width'], data['height'] = (int(d * data['hr_scale']) for d in data['init_images'][0].size)
        opts.upscaler_for_img2img = data['hr_upscaler']
        del data['enable_hr']
        del data['hr_scale']
        del data['hr_upscaler']
    return imgs


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

sd_folder_path = os.getcwd()

def lora_dir():
    return shared.cmd_opts.lora_dir or os.path.join(sd_folder_path, 'models', 'Lora')

def lyco_dir():
    return shared.cmd_opts.lyco_dir_backcompat or os.path.join(sd_folder_path, 'models', 'LyCORIS')

def embeddings_dir():
    return shared.cmd_opts.embeddings_dir or os.path.join(sd_folder_path, 'embeddings')

def basemodels_dir():
    return shared.cmd_opts.ckpt_dir or os.path.join(sd_folder_path, 'models', 'Stable-diffusion')
