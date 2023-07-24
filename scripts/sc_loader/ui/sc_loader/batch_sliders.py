import gradio as gr

from ..ui_part import UiPart
from ...process import NB_BATCHES, NB_REPEATS, NB_ITER

class BatchSliders(UiPart):
    def build_components(self):
        self.nb_repeats = gr.Slider(minimum=1.0, maximum=100.0, step=1.0, label='Nb repeats', value=1.0)
        self.nb_batches = gr.Slider(minimum=1.0, maximum=100.0, step=1.0, label='Nb batches', value=1.0)
        self.nb_iter = gr.Slider(minimum=1.0, maximum=8.0, step=1.0, label='Batch size', value=1.0)

    @property
    def components(self):
        return {
            NB_REPEATS: self.nb_repeats,
            NB_BATCHES: self.nb_batches,
            NB_ITER: self.nb_iter,
        }
