from contextlib import contextmanager

import gradio as gr

from modules import sd_models

from ...process import MODEL, SCENARIO, POSITIVE, NEGATIVE, TAGS
from ... import context as c

from ..ui_part import UiPart

@contextmanager
def col():
    with gr.Column(scale=1):
        with gr.Row():
            yield None

def get_prompts():
    return sorted([f'${prompt}' for prompt in c.database['prompts'].keys()])

def get_models():
    return [
        '--- Lists ---',
        *sorted(list(c.database['series']['models'].keys())),
        '--- Models ---',
        *sorted([model.split('.')[0] for model in sd_models.checkpoint_tiles()])
    ]

def get_scenarios():
    return [
        '--- Lists ---',
        *sorted(list(c.database['series']['scenarios'].keys())),
        '--- Scenarios ---',
        *sorted(list(c.database['scenarios'].keys()))
    ]

class MainInputs(UiPart):
    def switch_sc(self, scenario):
        try:
            data = c.database['scenarios'][c.database['series']['scenarios'][scenario][0]]
        except KeyError:
            data = c.database['scenarios'][scenario]

        expected_characters = data['characters']
        c.expected_characters_idxs = [c.database['character_types'].index(character) for character in expected_characters]
        return [*[
            gr.update(visible=i in c.expected_characters_idxs)
            for i in range(self.parent.nb_max_chars)
        ]]

    def build_components(self):
        with col():
            self.model = gr.Dropdown(
                label='Model',
                choices=get_models(),
                type='value'
            )
        with col():
            self.scenario = gr.Dropdown(
                label='Scenario',
                choices=get_scenarios(),
                type='value'
            )
        with col():
            self.positive = gr.Textbox(label='Positive')
        with col():
            self.negative = gr.Textbox(label='Negative')
        with col():
            self.tags = gr.Textbox(label='Tags')
        with col():
            self.expander_finder = gr.Dropdown(
                label='Expander finder',
                choices=get_prompts(),
                type='value'
            )

    def link_actions(self, after=False):
        if after:
            self.scenario.change(self.switch_sc, [self.scenario], [*self.parent.character_rows], queue=False)

    def reload_data(self):
        return [
            self.model,
            self.scenario,
            self.expander_finder
        ], [
            lambda: {'choices': get_models()},
            lambda: {'choices': get_scenarios()},
            lambda: {'choices': get_prompts()}
        ]

    @property
    def components(self):
        return {
            MODEL: self.model,
            SCENARIO: self.scenario,
            POSITIVE: self.positive,
            NEGATIVE: self.negative,
            TAGS: self.tags
        }
