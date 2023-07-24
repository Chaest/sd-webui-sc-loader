import os

import gradio as gr

from modules.ui_common import create_refresh_button
from modules.shared import opts

from ..ui_part import UiPart
from ... import context as c
from ...context import DB_DIR

class TypeAndFile(UiPart):
    def __init__(self, parent):
        super().__init__(parent)
        self.prompt_type = 'characters'

    def get_prompt_files(self):
        path_to_files = f'{opts.sc_loader_config_path}/{DB_DIR}/prompts/{self.prompt_type}'
        return [
            file_name
            for file_name in os.listdir(path_to_files)
            if any(file_name.endswith(ext) for ext in ('.yaml', '.yml'))
        ]

    def get_types(self):
        path_to_types = f'{opts.sc_loader_config_path}/{DB_DIR}/prompts'
        return [
            file_name
            for file_name in os.listdir(path_to_types)
            if os.path.isdir(path_to_types+'/'+file_name)
        ]

    def update_prompt_type(self, prompt_type):
        self.prompt_type = prompt_type
        return gr.update(choices=self.get_prompt_files())

    def build_components(self):
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    self.type_folder = gr.Dropdown(
                        label='Type',
                        choices=self.get_types(),
                        type='value'
                    )
                    create_refresh_button(
                        self.type_folder,
                        c.load_db,
                        lambda: {'choices': self.get_types()},
                        f'{self.parent.tab_name}_refresh_type_folder'
                    )

            with gr.Column(scale=1):
                with gr.Row():
                    self.char_file = gr.Dropdown(
                        label='File',
                        choices=self.get_prompt_files(),
                        type='value'
                    )
                    create_refresh_button(
                        self.char_file,
                        c.load_db,
                        lambda: {'choices': self.get_prompt_files()},
                        f'{self.parent.tab_name}_refresh_char_files'
                    )

    def link_actions(self):
        self.type_folder.change(
            fn=self.update_prompt_type,
            inputs=[self.type_folder],
            outputs=[self.char_file],
            queue=False
        )

    @property
    def components(self):
        return {
            'type_folder': self.type_folder,
            'char_file': self.char_file
        }
