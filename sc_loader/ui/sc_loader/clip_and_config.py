import gradio as gr

from modules.ui_components import FormRow
from modules.shared import opts

from ..ui_part import UiPart
from ...process.constants import USE_CLIP_SKIP, USE_CFG_SCALE, CLIP_SKIP, CFG_SCALE

class ClipAndConfig(UiPart):
    def build_components(self):
        with FormRow():
            self.use_clip_skip = gr.Checkbox(False, label='Use clip skip')
            self.use_scale = gr.Checkbox(False, label='Use scale')

        with FormRow():
            self.clip_skip = gr.Number(label='Clip skip', value=opts.CLIP_stop_at_last_layers)
            self.cfg_scale = gr.Slider(
                minimum=0.0,
                maximum=30.0,
                step=0.5,
                label='Cfg scale',
                value=7.0
            )

    @property
    def components(self):
        return {
            USE_CLIP_SKIP: self.use_clip_skip,
            USE_CFG_SCALE: self.use_scale,
            CLIP_SKIP: self.clip_skip,
            CFG_SCALE: self.cfg_scale
        }
