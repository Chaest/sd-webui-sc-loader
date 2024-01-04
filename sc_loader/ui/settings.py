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
                    'sc_loader_civitai_api_key': shared.OptionInfo(
                        '',
                        'API Key for civitAI model downloads',
                        gr.Textbox,
                        {'interactive': True}
                    ).info(f'If not set, no key provided.'),
                    'sc_loader_enable_models_presets': shared.OptionInfo(
                        False,
                        'Enable models\' presets feature',
                        gr.Checkbox,
                        {'interactive': True}
                    ).info(''),
                    'sc_loader_enable_lora_options': shared.OptionInfo(
                        False,
                        'Enable LoRA/LoCON suboptions',
                        gr.Checkbox,
                        {'interactive': True}
                    ).info(''),
                    'sc_loader_enable_ad_option': shared.OptionInfo(
                        False,
                        'Enable !A Detailer option',
                        gr.Checkbox,
                        {'interactive': True}
                    ).info('"AD" Checkbox'),
                    'sc_loader_enable_fe_option': shared.OptionInfo(
                        False,
                        'Enable Face Editor option',
                        gr.Checkbox,
                        {'interactive': True}
                    ).info('"FE" Checkbox'),
                    'sc_loader_enable_dbedit_option': shared.OptionInfo(
                        False,
                        'Enable database edit tab',
                        gr.Checkbox,
                        {'interactive': True}
                    ).info('Alternatively just use the A1111 tab options'),
                }
            )
        )
