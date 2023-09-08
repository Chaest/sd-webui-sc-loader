import os
import json

import yaml
import gradio as gr

from modules.shared import opts
from modules.ui_components import ToolButton
from modules.ui_common import refresh_symbol

from ...context import DB_DIR
from ..ui_part import UiPart

def list_db_files():
    all_files = []
    for root, _, files in os.walk(f'{opts.sc_loader_config_path}/{DB_DIR}'):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
    return all_files

def refresh(file_selector):
    with open(file_selector, 'r', encoding='utf-8') as f:
        content = f.read()

    return [gr.update(choices=list_db_files()), content]

def save(file_selector, file_editor):
    print(file_selector, '"'+file_editor+'"')
    if file_selector.endswith('.yaml') or file_selector.endswith('.yml'):
        try:
            yaml.safe_load(file_editor)
        except Exception as exc:
            return f'Invalid YAML: {exc}'
    elif file_selector.endswith('.json'):
        try:
            json.loads(file_editor)
        except Exception as exc:
            return f'Invalid JSON: {exc}'

    with open(file_selector, 'w', encoding='utf-8') as f:
        f.write(file_editor)

    return 'Successfully updated'

class Inputs(UiPart):
    def build_components(self):
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    self.file1 = gr.Dropdown(label='Pick File 1', choices=list_db_files(), type='value')
                    self.refresh1 = ToolButton(value=refresh_symbol)
            with gr.Column(scale=1):
                with gr.Row():
                    self.file2 = gr.Dropdown(label='Pick File 2', choices=list_db_files(), type='value')
                    self.refresh2 = ToolButton(value=refresh_symbol)
        with gr.Row():
            with gr.Column(scale=1):
                self.file1_editor = gr.Textbox(lines=30, label='')
            with gr.Column(scale=1):
                self.file2_editor = gr.Textbox(lines=30, label='')
        with gr.Row():
            with gr.Column(scale=1):
                self.save1 = gr.Button('Save')
            with gr.Column(scale=1):
                self.save2 = gr.Button('Save')
        with gr.Row():
            with gr.Column(scale=1):
                self.output1 = gr.HTML('Output', elem_classes='infotext')
            with gr.Column(scale=1):
                self.output2 = gr.HTML('Output', elem_classes='infotext')

    def link_actions(self):
        self.refresh1.click(
            fn=refresh,
            inputs=[self.file1],
            outputs=[self.file1, self.file1_editor]
        )
        self.refresh2.click(
            fn=refresh,
            inputs=[self.file2],
            outputs=[self.file2, self.file2_editor]
        )
        self.save1.click(
            fn=save,
            inputs=[self.file1, self.file1_editor],
            outputs=[self.output1]
        )
        self.save2.click(
            fn=save,
            inputs=[self.file2, self.file2_editor],
            outputs=[self.output2]
        )

    @property
    def components(self):
        return {
            'file1': self.file1,
            'refresh1': self.refresh1,
            'file1_editor': self.file1_editor,
            'save1': self.save1,
            'output1': self.output1,
            'file2': self.file2,
            'refresh2': self.refresh2,
            'file2_editor': self.file2_editor,
            'save2': self.save2,
            'output2': self.output2
        }
