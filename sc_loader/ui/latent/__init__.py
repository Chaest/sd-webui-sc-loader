import gradio as gr

from .inputs import Inputs

class LatentUI:
    def __init__(self):
        self.components = {}

    def build(self):
        with gr.Group() as ui_group:
            with gr.Accordion('Sc Latent Couple', open=False):
                self.components |= Inputs(self).build()

        return ui_group, [
            self.components['enabled'],
            self.components['divisions'],
            self.components['positions'],
            self.components['weights'],
            self.components['end_at_step'],
            self.components['pose']
        ]
