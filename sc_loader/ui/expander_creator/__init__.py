import gradio as gr

from .type_and_file import TypeAndFile
from .name_and_url import NameAndUrl
from .additionnal_inputs import AdditionnalInputs
from .validation import Validation

class PromptCreatorTab:
    tab_name = 'expander_creator'
    tab_title = 'Expander creation'

    def __init__(self):
        self.components = {}

    def build(self):
        with gr.Blocks(analytics_enabled=False) as ui_component:
            with gr.Row(variant='compact'):
                with gr.Column(scale=6):
                    self.components |= TypeAndFile(self).build()
                    self.components |= NameAndUrl(self).build()
                    self.components |= AdditionnalInputs(self).build()
                    self.components |= Validation(self).build()

            return [(ui_component, self.tab_title, self.tab_name)]
