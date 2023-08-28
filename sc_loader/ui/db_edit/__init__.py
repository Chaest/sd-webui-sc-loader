import gradio as gr

from .inputs import Inputs

class DBEditTab:
    tab_title = 'Sc DB Edit'
    tab_name = 'sc_db_edit'

    def __init__(self):
        self.components = {}

    def build(self):
        with gr.Blocks(analytics_enabled=False) as ui_component:
            self.components |= Inputs(self).build()

            return [(ui_component, self.tab_title, self.tab_name)]
