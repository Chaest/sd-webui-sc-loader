MODEL = 'model'
SCENARIO = 'scenario'
POSITIVE = 'positive'
NEGATIVE = 'negative'
TAGS = 'tags'
NB_REPEATS = 'nb_repeats'
NB_BATCHES = 'nb_batches'
NB_ITER = 'nb_iter'
RESTORE_F = 'restore_faces'
USE_HIRES = 'enable_hr'
UPSCALER = 'upscaler'
DENOISE_ST = 'strength'
UPSCALE_BY = 'upscale_scale'
USE_CLIP_SKIP = 'use_clip_skip'
CLIP_SKIP = 'clip_skip'
USE_CFG_SCALE = 'use_cfg_scale'
CFG_SCALE = 'cfg_scale'
USE_SAMPLER = 'use_sampler'
SAMPLER = 'sampler'
USE_STEPS = 'use_steps'
STEPS = 'steps'
SEED = 'seed'

CHARACTERS = 'DO NOT USE'

COMPONENT_ARG_ORDER = (
    MODEL, SCENARIO,
    POSITIVE, NEGATIVE,
    TAGS,
    NB_REPEATS, NB_BATCHES, NB_ITER,
    RESTORE_F,
    USE_HIRES, UPSCALER, DENOISE_ST, UPSCALE_BY,
    USE_CLIP_SKIP, CLIP_SKIP,
    USE_CFG_SCALE, CFG_SCALE,
    USE_SAMPLER, SAMPLER,
    USE_STEPS, STEPS,
    SEED
)
