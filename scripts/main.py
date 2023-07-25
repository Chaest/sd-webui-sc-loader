from modules import script_callbacks

from sc_loader.ui import ScLoaderTab, PromptCreatorTab, SettingsTab


scl_tab = ScLoaderTab()
pc_tag = PromptCreatorTab()
settings = SettingsTab()

script_callbacks.on_ui_settings(settings.build)
script_callbacks.on_ui_tabs(scl_tab.build)
script_callbacks.on_ui_tabs(pc_tag.build)
