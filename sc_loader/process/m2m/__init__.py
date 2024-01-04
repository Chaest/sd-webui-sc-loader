'''
    Code taken and adapted from https://github.com/Scholar01/sd-webui-mov2mov/tree/master
    In accordance to https://github.com/Scholar01/sd-webui-mov2mov/blob/master/LICENSE
    For simplification
'''

import os
import time

import imageio
import numpy as np
import cv2
from PIL import Image, ImageSequence

from modules import processing, shared
from modules.shared import state
from modules.processing import process_images
import modules.scripts as scripts

scripts_mov2mov = scripts.ScriptRunner()

def process_mov2mov(p, mov_file, movie_frames, max_frames, resize_mode, w, h, args):
    processing.fix_seed(p)
    images = get_mov_all_images(mov_file, movie_frames)
    if not images:
        print('Failed to parse the video, please check')
        return

    print(f'The video conversion is completed, images:{len(images)}')
    if max_frames == -1 or max_frames > len(images):
        max_frames = len(images)

    max_frames = int(max_frames)

    p.do_not_save_grid = True
    state.job_count = max_frames  # * p.n_iter
    generate_images = []
    for i, image in enumerate(images):
        if i >= max_frames:
            break

        state.job = f"{i + 1} out of {max_frames}"
        if state.skipped:
            state.skipped = False

        if state.interrupted:
            break

        img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 'RGB')

        p.init_images = [img] * p.batch_size
        proc = scripts_mov2mov.run(p, *args)
        if proc is None:
            print(f'current progress: {i + 1}/{max_frames}')
            processed = process_images(p)
            gen_image = processed.images[0]
            generate_images.append(gen_image)

    return save_video(generate_images, movie_frames)

def save_video(images, fps):
    out_dir = shared.opts.data.get('mov2mov_output_dir', 'outputs/mov2mov-videos')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    out_path =f'{out_dir}/{int(time.time())}.mp4'
    with imageio.v2.get_writer(out_path, format='ffmpeg', mode='I', fps=fps, codec='libx264') as writer:
        for img in images:
            writer.append_data(np.asarray(img))
    return out_path

class CustomVideoCapture:
    def __init__(self, path):
        if path.endswith('.mp4'):
            self.is_gif = False
            self.video = cv2.VideoCapture(path)
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
        else:
            self.is_gif = True
            self.gif = Image.open(path)
            self.frames = [frame.copy() for frame in ImageSequence.Iterator(self.gif)]
            self.current_frame = 0
            self.length = len(self.frames)
            self.fps = 10  # Default FPS for GIFs, adjust as necessary

    def read(self):
        if self.is_gif:
            if self.current_frame < self.length:
                pil_image = self.frames[self.current_frame]
                self.current_frame += 1
                opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                return True, opencv_image
            else:
                return False, None
        else:
            return self.video.read()

    def release(self):
        if not self.is_gif:
            self.video.release()

def get_mov_all_images(file, frames, rgb=False):
    cap = CustomVideoCapture(file)
    fps = cap.fps
    if frames > fps:
        print('Warning: The set number of frames is greater than the number of video frames')
        frames = int(fps)

    skip = max(1, fps // frames)
    count = 1
    fs = 1
    image_list = []
    while True:
        flag, frame = cap.read()
        if not flag:
            break
        else:
            if fs % skip == 0:
                if rgb and not file.endswith('.gif'):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_list.append(frame)
                count += 1
        fs += 1
    cap.release()
    return image_list
