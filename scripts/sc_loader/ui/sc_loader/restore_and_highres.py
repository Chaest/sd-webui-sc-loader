import gradio as gr

from modules.ui_components import FormRow, FormGroup
from modules import shared

from ..ui_part import UiPart
from ...process import RESTORE_F, USE_HIRES, UPSCALER, DENOISE_ST, UPSCALE_BY

class RestoreAndHires(UiPart):
    def build_components(self):
        with FormRow(elem_classes='checkboxes-row', variant='compact'):
            self.restore_faces = gr.Checkbox(label='Restore faces', value=False)
            self.enable_hr = gr.Checkbox(label='Hires. fix', value=False)

        with FormGroup(visible=False) as self.hr_options:
            self.upscaler = gr.Dropdown(
                label='Upscaler',
                choices=[*shared.latent_upscale_modes, *[x.name for x in shared.sd_upscalers]],
                value='R-ESRGAN 4x+',
                type='value'
            )
            self.scale = gr.Slider(
                minimum=1.0,
                maximum=4.0,
                step=0.05,
                label='Upscale by',
                value=2.5
            )
            self.strength = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                step=0.01,
                label='Denoising strength',
                value=0.37
            )

    def link_actions(self):
        self.enable_hr.change(
            fn=lambda val: gr.update(visible=val),
            inputs=[self.enable_hr],
            outputs=[self.hr_options],
            queue=False
        )

    @property
    def components(self):
        return {
            RESTORE_F: self.restore_faces,
            USE_HIRES: self.enable_hr,
            UPSCALER: self.upscaler,
            UPSCALE_BY: self.scale,
            DENOISE_ST: self.strength
        }
