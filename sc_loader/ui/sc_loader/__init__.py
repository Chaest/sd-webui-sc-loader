import gradio as gr

from modules.ui_common import create_output_panel
from modules.shared import opts
from modules.call_queue import wrap_gradio_gpu_call

from ... import context as c
from ...process.bob import bobing, COMPONENT_ARG_ORDER

from .batch_sliders import BatchSliders
from .buttons import Buttons
from .char_inputs import CharInputs
from .clip_and_config import ClipAndConfig
from .main_inputs import MainInputs
from .restore_and_highres import RestoreAndHires
from .sampler_section import SamplerSection
from .seed import Seed
from .title import Title

class ScLoaderTab:
    tab_title = 'Sc Loader'
    tab_name = 'sc_loader'

    def __init__(self):
        c.load_db()
        self.components = {}
        self.nb_max_chars = len(c.database['character_types'])
        self.components_to_refresh = []
        self.methods_to_refresh_them = []

    def submit_arguments(self):
        return [
            gr.Label(visible=False),
            *[self.components[component_key] for component_key in COMPONENT_ARG_ORDER],
            *self.characters,
            *self.char_prompts
        ]

    def handle_ui_part(self, part_cls):
        part = part_cls(self)
        self.components |= part.build()
        components, methods = part.reload_data()
        self.components_to_refresh += components
        self.methods_to_refresh_them += methods
        return part

    def handle_char_part(self):
        part = CharInputs(self)
        self.characters, self.char_prompts, self.character_rows = part.build()
        components, methods = part.reload_data()
        self.components_to_refresh += components
        self.methods_to_refresh_them += methods
        return part

    def build_components(self):
        with gr.Row(variant='compact'):
            with gr.Column(scale=6):
                with gr.Row():
                    self.title_part = self.handle_ui_part(Title)
                with gr.Row():
                    self.main_inputs = self.handle_ui_part(MainInputs)
                with gr.Row():
                    self.handle_char_part()

            with gr.Column(scale=1):
                with gr.Row(elem_classes='generate-box'):
                    self.handle_ui_part(Buttons)
                    self.handle_ui_part(BatchSliders)

        with gr.Row(equal_height=False):
            with gr.Column(variant='compact'):
                self.handle_ui_part(RestoreAndHires)
                self.handle_ui_part(ClipAndConfig)
                self.handle_ui_part(SamplerSection)
                self.handle_ui_part(Seed)

            return create_output_panel(self.tab_name, opts.outdir_txt2img_samples)

    def build(self):
        c.init()

        with gr.Blocks(analytics_enabled=False) as ui_component:
            txt2img_gallery, generation_info, html_info, html_log = self.build_components()

            self.components['submit'].click(
                fn=wrap_gradio_gpu_call(bobing, extra_outputs=[None, '', '']),
                _js='submit_sc_loader',
                inputs=self.submit_arguments(),
                outputs=[txt2img_gallery, generation_info, html_info, html_log],
                show_progress=False
            )

            self.main_inputs.link_actions(True)
            self.title_part.link_actions(self.components_to_refresh, self.methods_to_refresh_them)

            return [(ui_component, self.tab_title, self.tab_name)]
