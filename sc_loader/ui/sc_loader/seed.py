import gradio as gr

from modules.ui_components import FormRow

from ..ui_part import UiPart
from ...process import SEED

class Seed(UiPart):
    def build_components(self):
        with FormRow(variant='compact'):
            self.seed = gr.Number(label='Seed', value=-1)
            self.seed.style(container=False)

    @property
    def components(self):
        return {
            SEED: self.seed
        }
