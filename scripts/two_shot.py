import modules.scripts as scripts
from modules.scripts import AlwaysVisible
from modules.script_callbacks import on_cfg_denoised

from sc_loader.process.latent.params import params_to_filters
from sc_loader.process.latent.tensor import denoised_callback
from sc_loader.ui import LatentUI
from sc_loader import context as c

ENABLED = 0

class LatentScript(scripts.Script):
    def __init__(self):
        self.ui_root = None
        self.callbacks_added = False

    def title(self):
        return 'Sc Latent Couple'

    def show(self, _):
        return AlwaysVisible

    def ui(self, _):
        ui_group, params = LatentUI().build()
        self.ui_root = ui_group
        return params

    def process(self, sd_proc, *args):
        enabled, divisions, positions, weights, end_at_step = args[0:5]
        pose_masks = args[5] if len(args) == 6 else None

        if not enabled:
            c.denoise_args = (False, None, None, None)
            return

        c.denoise_args = (
            enabled,
            params_to_filters(divisions, positions, weights, pose_masks),
            sd_proc.batch_size,
            end_at_step
        )

        if not self.callbacks_added:
            on_cfg_denoised(denoised_callback)
            self.callbacks_added = True
