import os

import yaml
import gradio as gr

from modules.ui import save_style_symbol, refresh_symbol
from modules.ui_components import InputAccordion, ToolButton

from ... import context as c
from ...process.constants import *
from ..ui_part import UiPart

NB_COMP_BEFORE_CHARS = len(COMPONENT_ARG_ORDER)

def get_presets():
    presets_path = f'{c.get_cfg_path()}/presets'
    if not os.path.exists(presets_path):
        return []
    return [
        preset_filename.split('.')[0]
        for preset_filename in os.listdir(presets_path)
        if preset_filename.endswith('.yaml')
    ]

def get_char_names_and_prompts(components):
    characters_data = components[NB_COMP_BEFORE_CHARS:]
    middle = int(len(characters_data) / 2)
    return characters_data[:middle], characters_data[middle:]

def get_component(components, name):
    if name not in COMPONENT_ARG_ORDER:
        return get_char_names_and_prompts(components)
    return components[COMPONENT_ARG_ORDER.index(name)]

def idx_to_type(char_idx):
    return c.database['character_types'][char_idx]

def save_preset(name, *components):
    presets_path = f'{c.get_cfg_path()}/presets'
    if not os.path.exists(presets_path):
        os.makedirs(presets_path)

    preset_path = f'{presets_path}/{name}.yaml'
    if os.path.exists(preset_path):
        return f'Preset already exists at {preset_path}'

    data = {
        COMPONENT_ARG_ORDER[component_idx]: component_value
        for component_idx, component_value in enumerate(components[:NB_COMP_BEFORE_CHARS])
    }
    data['characters'] = {}
    for char_idx, (char_name, char_prompt) in enumerate(zip(*get_char_names_and_prompts(components))):
        char_type = idx_to_type(char_idx)
        data['characters'][char_type] = {
            'name': char_name,
            'prompt': char_prompt
        }

    with open(preset_path, 'w', encoding='utf-8') as preset_file:
        yaml.dump(data, preset_file)

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
    for character_type in c.database['character_types']:
        character = data.get('characters', {}).get(character_type, empty)
        character_names.append(character['name'])
        character_prompts.append(character['prompt'])

    component_values += character_names
    component_values += character_prompts

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
                self.preset_output = gr.HTML(' ')

    def reload_data(self):
        return [self.preset_pick], [lambda: {'choices': get_presets()}]

    def link_actions(self, after=False):
        if after:
            components = self.parent.submit_arguments()[1:]
            self.preset_saver.click(fn=save_preset, inputs=[self.preset_name, *components], outputs=[self.preset_output])
            self.preset_loader.click(fn=load_preset, inputs=[self.preset_pick], outputs=[self.preset_output, self.preset_pick, *components])

    @property
    def components(self):
        return {
            'preset_pick': self.preset_pick,
            'preset_loader': self.preset_loader,
            'preset_name': self.preset_name,
            'preset_saver': self.preset_saver
        }
