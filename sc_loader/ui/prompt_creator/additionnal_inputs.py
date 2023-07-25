import gradio as gr

from ..ui_part import UiPart

class AdditionnalInputs(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=80):
                self.prompt = gr.Textbox(label='Additional prompts')
        with gr.Row():
            with gr.Column(scale=1):
                self.weight = gr.Slider(
                    minimum=-2.0,
                    maximum=2.0,
                    step=0.05,
                    label='Model weight',
                    value=0.75
                )

    @property
    def components(self):
        return {
            'prompt': self.prompt,
            'weight': self.weight
        }
