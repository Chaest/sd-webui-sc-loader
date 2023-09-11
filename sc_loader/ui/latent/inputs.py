import os

import gradio as gr

from modules.ui_common import create_refresh_button

from sc_loader.process.latent.tensor import do_visualize

from ..ui_part import UiPart
from ...context import get_cfg_path

def get_pose_files():
    poses = []
    for root, _, files in os.walk(get_cfg_path()):
        for file in files:
            if file.split('.')[-1] in ('json', 'yaml', 'yaml'):
                poses.append(os.path.join(root, file))
    return poses

class Inputs(UiPart):
    def build_components(self):
        self.enabled = gr.Checkbox(value=False, label='Enabled')
        with gr.Row():
            self.divisions = gr.Textbox(label='Divisions', value='1:1,1:2,1:2')
            self.positions = gr.Textbox(label='Positions', value='0:0,0:0,0:1')
        with gr.Row():
            self.weights = gr.Textbox(label='Weights', value='0.2,0.8,0.8')
            self.end_at_step = gr.Slider(minimum=0, maximum=150, step=1, label='end at this step', value=150)
        with gr.Row():
            self.pose = gr.Dropdown(
                label='Pose',
                choices=get_pose_files(),
                type='value'
            )
            create_refresh_button(
                self.pose,
                lambda: None,
                lambda: {'choices': get_pose_files()},
                f'latent_refresh_poses'
            )
        self.visualize_button = gr.Button(value='Visualize')
        self.visual_regions = gr.Gallery(label='Regions', columns=(4, 4, 4, 8), height='auto')

        self.visualize_button.click(fn=do_visualize, inputs=[self.divisions, self.positions, self.weights, self.pose], outputs=[self.visual_regions])

    @property
    def components(self):
        return {
            'enabled': self.enabled,
            'divisions': self.divisions,
            'positions': self.positions,
            'weights': self.weights,
            'end_at_step': self.end_at_step,
            'visualize_button': self.visualize_button,
            'visual_regions': self.visual_regions,
            'pose': self.pose
        }
