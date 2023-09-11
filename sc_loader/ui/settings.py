import os

import gradio as gr

from modules import shared, scripts

class SettingsTab:
    def build(self):
        default_path = os.path.join(scripts.current_basedir, 'base_configs')
        shared.options_templates.update(
            shared.options_section(
                ('sc_loader', 'Scenario loader'),
                {
                    'sc_loader_config_path': shared.OptionInfo(
                        default_path,
                        'Custom path to configuration',
                        gr.Textbox,
                        {'interactive': True}
                    ).info(f'Defaults to "{default_path}"'),
                }
            )
        )
