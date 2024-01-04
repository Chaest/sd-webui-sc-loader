import os

import yaml
import gradio as gr

from modules.ui import save_style_symbol, refresh_symbol
from modules.ui_components import InputAccordion, ToolButton
from modules.shared import opts

from ... import context as c
from ...process.constants import *
from ..ui_part import UiPart

NB_COMP_BEFORE_CHARS = len(COMPONENT_ARG_ORDER)

def get_presets():
    presets_path = f'{c.get_cfg_path()}/presets'
    if not os.path.exists(presets_path):
        return []
    return [
        preset_filename.replace('.yaml', '').replace('.yml', '')
        for preset_filename in os.listdir(presets_path)
        if preset_filename.endswith('.yaml')
    ]

def get_char_data(nb_char, components):
    start_char = NB_COMP_BEFORE_CHARS
    start_prompts = start_char + nb_char
    start_weights = start_prompts + nb_char
    start_comopts = start_weights + nb_char
    return (
        components[start_char:start_prompts],
        components[start_prompts:start_weights],
        components[start_weights:start_comopts],
        components[start_comopts:],
    )

def get_component(nb_char, components, name):
    if name not in COMPONENT_ARG_ORDER:
        return get_char_data(nb_char, components)
    return components[COMPONENT_ARG_ORDER.index(name)]

def idx_to_type(char_idx):
    return c.database['character_types'][char_idx]

def save_preset(nb_char, name, overwrite, *components):
    presets_path = f'{c.get_cfg_path()}/presets'
    if not os.path.exists(presets_path):
        os.makedirs(presets_path)

    preset_path = f'{presets_path}/{name}.yaml'
    if os.path.exists(preset_path) and not overwrite:
        return f'Preset already exists at {preset_path}'

    data = {
        COMPONENT_ARG_ORDER[component_idx]: component_value
        for component_idx, component_value in enumerate(components[:NB_COMP_BEFORE_CHARS])
    }
    data['characters'] = {}
    for char_idx, (char_name, char_prompt, char_weight, char_comopt) in enumerate(zip(*get_char_data(nb_char, components))):
        char_type = idx_to_type(char_idx)
        data['characters'][char_type] = {
            'name': char_name,
            'prompt': char_prompt,
            'weight': char_weight,
            'comopt': char_comopt
        }

    with open(preset_path, 'w', encoding='utf-8') as preset_file:
        yaml.dump(data, preset_file)

    return f'Successfully created preset at {preset_path}'

def save_model_preset(overwrite, *components):
    presets_path = f'{c.get_cfg_path()}/_db/model_presets'
    if not os.path.exists(presets_path):
        os.makedirs(presets_path)

    full_data = {
        COMPONENT_ARG_ORDER[component_idx]: component_value
        for component_idx, component_value in enumerate(components[:NB_COMP_BEFORE_CHARS])
    }

    model_name = full_data['model']

    preset_path = f'{presets_path}/{model_name}.yaml'
    if os.path.exists(preset_path) and not overwrite:
        return f'Preset already exists at {preset_path}'

    data = {
        'positive': full_data['positive'],
        'negative': full_data['negative']
    }

    if full_data['use_cfg_scale']:
        data['cfg_scale'] = full_data['cfg_scale']
    if full_data['use_sampler']:
        data['sampler'] = full_data['sampler']
    if full_data['use_steps']:
        data['steps'] = full_data['steps']
    if full_data['enable_hr']:
        data['upscaler'] = full_data['upscaler']
        data['upscale_scale'] = full_data['upscale_scale']
        data['strength'] = full_data['strength']

    with open(preset_path, 'w', encoding='utf-8') as preset_file:
        yaml.dump({model_name: data}, preset_file)

    return f'Successfully created preset at {preset_path}'

def load_preset(name):
    preset_path = f'{c.get_cfg_path()}/presets/{name}.yaml'
    if not os.path.exists(preset_path):
        return f'No preset found at {preset_path}'

    with open(preset_path, encoding='utf-8') as preset_file:
        data = yaml.safe_load(preset_file)

    component_values = [
        data[component_name] if component_name in data else None
        for component_name in COMPONENT_ARG_ORDER
    ]

    empty = {'name': '', 'prompt': ''}

    character_names = []
    character_prompts = []
    character_weights = []
    character_comopts = []
    for character_type in c.database['character_types']:
        character = data.get('characters', {}).get(character_type, empty)
        character_names.append(character['name'])
        character_prompts.append(character.get('prompt', ''))
        character_weights.append(character.get('weight', 1.0))
        character_comopts.append(character.get('comopt', ''))

    component_values += character_names
    component_values += character_prompts
    component_values += character_weights
    component_values += character_comopts

    return [f'Loaded {preset_path}', gr.update(choices=get_presets()), *component_values]

class PresetMenu(UiPart):
    def build_components(self):
        with InputAccordion(False, label='Presets'):
            with gr.Row():
                self.preset_pick = gr.Dropdown(
                    label='Load preset',
                    choices=get_presets(),
                    type='value'
                )
                self.preset_loader = ToolButton(value=refresh_symbol)
            with gr.Row():
                self.preset_name = gr.Textbox(label='Save preset')
                self.preset_saver = ToolButton(value=save_style_symbol)
            with gr.Row():
                self.overwrite = gr.Checkbox(False, label='Overwrite')
            with gr.Row(visible=opts.sc_loader_enable_models_presets):
                self.model_preset_title = gr.HTML('<h2>Save model preset<h2>')
                self.model_preset_saver = ToolButton(label='Save preset', value=save_style_symbol)
                self.enable_models_presets = gr.Checkbox(False, label='Enable models presets')
            with gr.Row():
                self.preset_output = gr.HTML(' ')

    def reload_data(self):
        return [self.preset_pick], [lambda: {'choices': get_presets()}]

    def link_actions(self, after=False):
        if after:
            components = self.parent.submit_arguments()[1:]
            def _save_preset(*args):
                return save_preset(self.parent.nb_max_chars, *args)
            self.preset_saver.click(fn=_save_preset, inputs=[self.preset_name, self.overwrite, *components], outputs=[self.preset_output])
            self.model_preset_saver.click(fn=save_model_preset, inputs=[self.overwrite, *components], outputs=[self.preset_output])
            self.preset_loader.click(fn=load_preset, inputs=[self.preset_pick], outputs=[self.preset_output, self.preset_pick, *components])

    @property
    def components(self):
        return {
            'preset_pick': self.preset_pick,
            'preset_loader': self.preset_loader,
            'preset_name': self.preset_name,
            'preset_saver': self.preset_saver,
            'enable_models_presets': self.enable_models_presets
        }
