import os
import gradio as gr
from modules import script_callbacks, shared, scripts

default_sc_loader_config_path = os.path.join(scripts.current_basedir, 'base_configs')
shared.options_templates.update(shared.options_section(('sc_loader', 'Scenario loader'), {
    "sc_loader_config_path_custom": shared.OptionInfo("", "Custom path to configuration", gr.Textbox, {'interactive': True}).info(f'Defaults to "{default_sc_loader_config_path}"'),
}))
shared.opts.sc_loader_config_path = shared.opts.sc_loader_config_path_custom if shared.opts.sc_loader_config_path_custom else default_sc_loader_config_path

from sc_loader.ui import ScLoaderTab, PromptCreatorTab, SettingsTab, ToolsTab, DBEditTab

scl_tab = ScLoaderTab()
pc_tag = PromptCreatorTab()
# settings = SettingsTab()
tools = ToolsTab()
db_edit = DBEditTab()

# script_callbacks.on_ui_settings(settings.build)
script_callbacks.on_ui_tabs(scl_tab.build)
script_callbacks.on_ui_tabs(pc_tag.build)
script_callbacks.on_ui_tabs(tools.build)
script_callbacks.on_ui_tabs(db_edit.build)
