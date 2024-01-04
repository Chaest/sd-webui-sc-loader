import torch
import torch.nn.functional as F

from modules import devices

COLORS = [
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (192, 192, 192),
    (255, 165, 0)
]

def create_filter(divisions, positions, weight, masks):
    return MultipleRectFilter(divisions, positions, weight) if isinstance(divisions, list) else PoseFilter(masks[divisions], positions, weight)

class MultipleRectFilter:
    def __init__(self, divisions, positions, weight):
        self.divisions_and_positions = list(zip(divisions, positions))
        self.weight = weight

    def create_tensor(self, num_channels, height_b, width_b):

        x = torch.zeros(num_channels, height_b, width_b).to(devices.device)

        for division, position in self.divisions_and_positions:
            division_height = height_b / division.y
            division_width = width_b / division.x
            y1 = int(division_height * position.y)
            y2 = int(division_height * position.ey)
            x1 = int(division_width * position.x)
            x2 = int(division_width * position.ex)

            x[:, y1:y2, x1:x2] = self.weight

        return x

class PoseFilter:
    def __init__(self, pose, radius, weight):
        self.pose = pose
        self.radius = radius
        self.weight = weight

    def create_tensor(self, num_channels, height_b, width_b):
        x = torch.zeros(num_channels, height_b, width_b).to(devices.device)

        mask_tensor = torch.from_numpy(self.pose).to(devices.device).float() * self.weight
        mask_tensor = mask_tensor.unsqueeze(0).unsqueeze(0)
        _, target_height, target_width = x.shape
        mask_tensor = F.interpolate(mask_tensor, size=(target_height, target_width), mode='nearest-exact')

        return x + mask_tensor.squeeze(0).expand_as(x)
