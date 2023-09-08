from .common import PARTS

def load_people(data):
    return [
        Person(person['pose_keypoints_2d']).data
        for person in data['people']
    ]

class Person:
    def __init__(self, data):
        if isinstance(data, list):
            it = iter(data)
            parts = list(zip(it, it, it))
            self.parts = {
                PARTS[i]: {
                    'layer': 0,
                    'coordinates': [part[0], part[1]],
                    'confidence': part[2]
                }
                for i, part in enumerate(parts)
            }
            self.size = 1
        elif isinstance(data, dict):
            self.size = data['size']
            self.parts = data['parts']

    @property
    def data(self):
        return {
            'size': self.size,
            'parts': {
                part_name: {
                    'layer': part_values['layer'],
                    'coordinates': part_values['coordinates']
                }
                for part_name, part_values in self.parts.items()
                if part_values.get('confidence', 1) > 0
            }
        }
