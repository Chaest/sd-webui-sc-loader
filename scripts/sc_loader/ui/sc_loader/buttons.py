import gradio as gr

from modules import shared

from ... import context as c
from ..ui_part import UiPart

class Buttons(UiPart):
    def build_components(self):
        self.submit = gr.Button('Generate', variant='primary')
        self.skip_batch = gr.Button('Skip batch')
        self.skip_model = gr.Button('Skip model')
        self.hard_skip = gr.Button('Hard Skip')

    def link_actions(self):
        def hard_skip():
            c.hard_skip_toggled = True
            shared.state.skip()
            shared.state.interrupt()

        def skip_model():
            c.skip_model = True
            shared.state.skip()
            shared.state.interrupt()

        self.skip_batch.click(fn=shared.state.skip)
        self.skip_model.click(fn=skip_model)
        self.hard_skip.click(fn=hard_skip)

    @property
    def components(self):
        return {
            'submit': self.submit,
            'skip_bach': self.skip_batch,
            'skip_model': self.skip_model,
            'hard_skip': self.hard_skip,
        }
