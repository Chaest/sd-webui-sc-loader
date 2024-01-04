import re

import gradio as gr

from modules.shared import opts

from ... import context as c
from ...payload.scripts.composable_lora import COMP_OPTS
from ..ui_part import UiPart

LORA_IC_RGXP = r'.*<(?:lora|lyco):(?:[^:]+):([^>]+)>.*'
DEFAULT_COMOPT = ''
DEFAULT_COMOPTS = gr.update(visible=False), 1.0, DEFAULT_COMOPT

char_opt_cache = {}

def get_chars():
    return [
        '--- Lists ---',
        *sorted(list(c.database['series'].get('characters', {}).keys())),
        '--- Characters ---',
        *sorted(list(c.database['prompts']['characters'].keys()))
    ]

def update_char_opts(character, idx):
    if not opts.sc_loader_enable_lora_options or character not in c.database['prompts']['characters']:
        return DEFAULT_COMOPTS
    char_prompt = c.database['prompts']['characters'][character]
    if isinstance(char_prompt, list):
        char_prompt = char_prompt[0]
    m = re.match(LORA_IC_RGXP, char_prompt)
    if not m:
        char_opt_cache[idx] = False
        return DEFAULT_COMOPTS
    weight = float(m[1])
    option = DEFAULT_COMOPT
    for opt_name, opt_data in COMP_OPTS.items():
        if re.match(opt_data['rgxp'], char_prompt):
            option = opt_name
            break
    char_opt_cache[idx] = True
    return gr.update(visible=True), weight, option

def fu(f, i):
    return lambda c: f(c, i)

class CharInputs(UiPart):
    def build_components(self):
        self.characters = [None] * self.parent.nb_max_chars
        self.character_pickers = [None] * self.parent.nb_max_chars
        self.character_prompts = [None] * self.parent.nb_max_chars
        self.character_options = [None] * self.parent.nb_max_chars
        self.character_weights = [None] * self.parent.nb_max_chars
        self.character_comopts = [None] * self.parent.nb_max_chars
        with gr.Column(scale=80):
            for i in range(self.parent.nb_max_chars):
                with gr.Row(visible=False) as self.character_pickers[i]:
                    self.characters[i] = gr.Dropdown(
                        label=c.database['character_types'][i],
                        choices=get_chars(),
                        type='value'
                    )
                    self.character_prompts[i] = gr.Textbox(label='')
                with gr.Row(visible=False) as self.character_options[i]:
                    self.character_weights[i] = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        step=0.05,
                        label='Weight  ',
                        value=1.0,
                        elem_id=f'weight-c{i}',
                        interactive=True
                    )
                    self.character_comopts[i] = gr.Dropdown(
                        label='Composable operations ',
                        choices=['']+list(COMP_OPTS.keys()),
                        elem_id=f'clop-c{i}',
                        interactive=True
                    )
        for i in range(self.parent.nb_max_chars):
            self.characters[i].change(
                fu(update_char_opts, i),
                [self.characters[i]],
                [self.character_options[i], self.character_weights[i], self.character_comopts[i]],
                queue=False
            )

    def reload_data(self):
        return self.characters, ([lambda: {'choices': get_chars()}] * self.parent.nb_max_chars)

    @property
    def components(self):
        return (
            self.characters,
            self.character_prompts,
            self.character_pickers,
            self.character_options,
            self.character_weights,
            self.character_comopts,
        )
