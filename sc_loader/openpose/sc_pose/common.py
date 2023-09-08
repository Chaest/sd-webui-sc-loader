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
