import gradio as gr

from modules import sd_models
from modules.ui_common import refresh_symbol
from modules.ui_components import ToolButton

from ... import context as c

from ..ui_part import UiPart

class Title(UiPart):
    def refresh_function(self, methods):
        def refresh():
            c.load_db()
            sd_models.list_models()
            return [gr.update(**method()) for method in methods]
        return refresh

    def build_components(self):
        with gr.Column(scale=100):
            with gr.Row():
                gr.HTML(value=f'<h1>Scenario Loader {c.version}</h1>')
                self.refresh_button = ToolButton(value=refresh_symbol)

    def link_actions(self, components=None, methods=None):
        if components and methods:
            self.refresh_button.click(fn=self.refresh_function(methods), inputs=[], outputs=components)

    @property
    def components(self):
        return {
            'refresh_button': self.refresh_button
        }
