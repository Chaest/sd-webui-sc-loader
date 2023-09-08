import gradio as gr

from ..ui_part import UiPart

class AdditionnalInputs(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=80):
                self.prompt = gr.Textbox(label='Additional positive prompts')
                self.negative_prompt = gr.Textbox(label='Additional negative prompts')
        with gr.Row():
            with gr.Column(scale=1):
                self.weight = gr.Slider(minimum=-7.0, maximum=7.0, step=0.05, label='Model weight  ', value=0.75)

    @property
    def components(self):
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'weight': self.weight
        }
