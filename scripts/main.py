from modules import script_callbacks
from modules.shared import opts

from sc_loader.ui import ScLoaderTab, PromptCreatorTab, SettingsTab, ToolsTab, DBEditTab

settings = SettingsTab()
scl_tab = ScLoaderTab()
pc_tag = PromptCreatorTab()
tools = ToolsTab()
db_edit = DBEditTab()

script_callbacks.on_ui_settings(settings.build)
script_callbacks.on_ui_tabs(scl_tab.build)
script_callbacks.on_ui_tabs(pc_tag.build)
script_callbacks.on_ui_tabs(tools.build)
if opts.sc_loader_enable_dbedit_option:
    script_callbacks.on_ui_tabs(db_edit.build)
