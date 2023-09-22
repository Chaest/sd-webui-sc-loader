import gradio as gr

from modules.ui_components import FormRow
from modules.sd_samplers import samplers

from ..ui_part import UiPart
from ...process.constants import USE_SAMPLER, SAMPLER, USE_STEPS, STEPS

class SamplerSection(UiPart):
    def build_components(self):
        with FormRow():
            self.override_sampler = gr.Checkbox(False, label='Override sampler')
            self.override_steps = gr.Checkbox(False, label='Override sampling steps')
        with FormRow():
            self.sampler = gr.Dropdown(
                label='Sampler',
                choices=[sampler.name for sampler in samplers],
                value='DPM++ 2M Karras',
                type='value'
            )
            self.steps = gr.Slider(
                minimum=1,
                maximum=150,
                step=1,
                label='Sampling steps',
                value=20
            )

    @property
    def components(self):
        return {
            USE_SAMPLER: self.override_sampler,
            USE_STEPS: self.override_steps,
            SAMPLER: self.sampler,
            STEPS: self.steps
        }
