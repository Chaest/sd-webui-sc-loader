import gradio as gr

from ..ui_part import UiPart

class NameAndUrl(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    self.char_name = gr.Textbox(label='Name')

            with gr.Column(scale=4):
                with gr.Row():
                    self.civitai_url = gr.Textbox(label='URL')

    @property
    def components(self):
        return {
            'char_name': self.char_name,
            'civitai_url': self.civitai_url
        }
