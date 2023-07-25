import gradio as gr

from modules import shared

class SettingsTab:
    def build(self):
        section = ('sc_loader', 'Scenario loader')
        shared.opts.add_option(
            'sc_loader_config_path',
            shared.OptionInfo(
                'extensions/sd-webui-sc-loader/base_configs',
                'Path to configuration',
                gr.Textbox,
                {'interactive': True},
                section=section
            )
        )
