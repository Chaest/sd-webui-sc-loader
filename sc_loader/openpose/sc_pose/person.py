from .common import PARTS, HAND_PARTS

def load_people(data):
    return [
        Person(person).data
        for person in data['people']
    ]

def pl_to_pd(points, names):
    if points is None: return {}
    it = iter(points)
    parts = list(zip(it, it, it))
    print(points, names)
    return {
        names[i]: {
            'layer': 0,
            'coordinates': [part[0], part[1]]
        }
        for i, part in enumerate(parts)
        if part[2] > 0
    }

class Person:
    def __init__(self, data):
        if isinstance(data.get('pose_keypoints_2d'), list):
            self.parts = pl_to_pd(data.get('pose_keypoints_2d'), PARTS)
            self.handle_hands_and_face(data)
            self.size = 1
        elif isinstance(data, dict):
            self.size = data['size']
            self.parts = data['parts']
            self.left_hand = data.get('left_hand')
            self.right_hand = data.get('right_hand')
            self.face = data.get('face')

    def handle_hands_and_face(self, data):
        self.left_hand = pl_to_pd(data.get('hand_left_keypoints_2d'), HAND_PARTS)
        self.right_hand = pl_to_pd(data.get('hand_right_keypoints_2d'), HAND_PARTS)
        if data.get('face_keypoints_2d'):
            it = iter(data['face_keypoints_2d'])
            self.face = {'layer': 0, 'points': [[l[0], l[1]] for l in zip(it, it, it) if l[2] > 0]}
        else:
            self.face = None

    @property
    def additionnal_body_parts(self):
        abp = {}
        if self.left_hand:
            abp['left_hand'] = self.left_hand
        if self.right_hand:
            abp['right_hand'] = self.right_hand
        if self.face:
            abp['face'] = self.face
        return abp

    @property
    def data(self):
        print(self.parts)
        return {
            'size': self.size,
            'parts': self.parts
        } | self.additionnal_body_parts
