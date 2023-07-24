import os
import sys

from modules import script_callbacks

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)

from sc_loader.ui import ScLoaderTab, PromptCreatorTab, SettingsTab # pylint: disable=wrong-import-position

scl_tab = ScLoaderTab()
pc_tag = PromptCreatorTab()
settings = SettingsTab()

script_callbacks.on_ui_settings(settings.build)
script_callbacks.on_ui_tabs(scl_tab.build)
script_callbacks.on_ui_tabs(pc_tag.build)
