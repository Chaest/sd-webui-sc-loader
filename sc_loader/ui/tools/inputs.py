import gradio as gr

from sc_loader.process.db import copy_db, add_file_to_db
from sc_loader.process.download import handle_batch, generic_handler, generic_updater
from sc_loader.openpose.sc_pose.sc_pose import openpose_to_scpose
from ..ui_part import UiPart

NOT_IMPLEMENTED = lambda _: 'Not implemented'
ACTIONS = [
    handle_batch,
    openpose_to_scpose,
    generic_handler,
    generic_updater,
    add_file_to_db,
    copy_db
]

def do_action(action, value):
    return ACTIONS[action](value)

class Inputs(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=1):
                self.action = gr.Dropdown(
                    label='Action',
                    choices=[
                        'Download batch',
                        'Openpose to ScPose',
                        'Download base model/pose/wildcard/package',
                        'Update pose/wildcard/package',
                        'Create file in db',
                        'Create db'
                    ],
                    type='index'
                )
                self.value = gr.Textbox()
        with gr.Row():
            with gr.Column(scale=1):
                self.submit = gr.Button('Gooo!', variant='primary')
        with gr.Row():
            with gr.Column(scale=1):
                self.output = gr.HTML('Output', elem_classes='infotext')

    def link_actions(self):
        self.submit.click(
            fn=do_action,
            inputs=[self.action, self.value],
            outputs=[self.output]
        )

    @property
    def components(self):
        return {
            'action': self.action,
            'value': self.value,
            'submit': self.submit,
            'output': self.output
        }
