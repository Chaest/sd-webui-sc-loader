from ..default_data import DEFAULT_RADIUS

COLORS = {
    'nose': [0, 0, 255],
    'neck': [255, 0, 0],
    'right_shoulder': [255, 170, 0],
    'right_elbow': [255, 255, 0],
    'right_wrist': [255, 85, 0],
    'left_shoulder': [170, 255, 0],
    'left_elbow': [85, 255, 0],
    'left_wrist': [0, 255, 0],
    'right_hip': [0, 255, 85],
    'right_knee': [0, 255, 170],
    'right_ankle': [0, 255, 255],
    'left_hip': [0, 170, 255],
    'left_knee': [0, 85, 255],
    'left_ankle': [85, 0, 255],
    'right_eye': [170, 0, 255],
    'left_eye': [255, 0, 255],
    'right_ear': [255, 0, 170],
    'left_ear': [255, 0, 85]
}

PARTS = list(COLORS.keys())

CONNECTIONS = (
    ( 'nose',           'neck'           ),
    ( 'nose',           'right_eye'      ),
    ( 'nose',           'left_eye'       ),
    ( 'right_eye',      'right_ear'      ),
    ( 'left_eye',       'left_ear'       ),
    ( 'neck',           'right_shoulder' ),
    ( 'neck',           'left_shoulder'  ),
    ( 'neck',           'right_hip'      ),
    ( 'neck',           'left_hip'       ),
    ( 'right_shoulder', 'right_elbow'    ),
    ( 'left_shoulder',  'left_elbow'     ),
    ( 'right_elbow',    'right_wrist'    ),
    ( 'left_elbow',     'left_wrist'     ),
    ( 'right_hip',      'right_knee'     ),
    ( 'left_hip',       'left_knee'      ),
    ( 'right_knee',     'right_ankle'    ),
    ( 'left_knee',      'left_ankle'     ),
)

HAND_POINTS_COLOR = [0, 0, 255]

HAND_CONNECTIONS = (
    ('wrist',   'thumb1',  [255, 0, 0]   ),
    ('thumb1',  'thumb2',  [255, 85, 0]  ),
    ('thumb2',  'thumb3',  [255, 170, 0] ),
    ('thumb3',  'thumb4',  [255, 255, 0] ),
    ('wrist',   'index1',  [170, 255, 0] ),
    ('index1',  'index2',  [85, 255, 0]  ),
    ('index2',  'index3',  [0, 255, 0]   ),
    ('index3',  'index4',  [0, 255, 85]  ),
    ('wrist',   'middle1', [0, 255, 170] ),
    ('middle1', 'middle2', [0, 255, 255] ),
    ('middle2', 'middle3', [0, 170, 255] ),
    ('middle3', 'middle4', [0, 85, 255]  ),
    ('wrist',   'ring1',   [0, 0, 255]   ),
    ('ring1',   'ring2',   [85, 0, 255]  ),
    ('ring2',   'ring3',   [170, 0, 255] ),
    ('ring3',   'ring4',   [255, 0, 255] ),
    ('wrist',   'pinky1',  [255, 0, 170] ),
    ('pinky1',  'pinky2',  [255, 0, 85]  ),
    ('pinky2',  'pinky3',  [255, 0, 0]   ),
    ('pinky3',  'pinky4',  [255, 85, 0]  ),
)

HAND_PARTS = (
    'wrist',
    'thumb1',  'thumb2',  'thumb3',  'thumb4',
    'index1',  'index2',  'index3',  'index4',
    'middle1', 'middle2', 'middle3', 'middle4',
    'ring1',   'ring2',   'ring3',   'ring4',
    'pinky1',  'pinky2',  'pinky3',  'pinky4',
)
