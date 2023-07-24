import gradio as gr

from ..ui_part import UiPart
from ...process.prompt_creation import create_character

class Validation(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=1):
                self.submit = gr.Button('Create prompt', variant='primary')
        with gr.Row():
            with gr.Column(scale=1):
                self.output = gr.HTML(elem_classes='infotext')

    def link_actions(self):
        self.submit.click(
            fn=create_character,
            inputs=[
                self.parent.components['char_file'],
                self.parent.components['char_name'],
                self.parent.components['civitai_url'],
                self.parent.components['prompt'],
                self.parent.components['weight'],
                self.parent.components['type_folder']
            ],
            outputs=[self.output]
        )

    @property
    def components(self):
        return {
            'submit': self.submit,
            'output': self.output
        }
