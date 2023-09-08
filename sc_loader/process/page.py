from PIL import Image, ImageDraw, ImageFont

from .. import context as c

MIN_NB_LINES = 1
MAX_NB_LINES = 3

PAGE_WIDTH = 1100
PAGE_HEIGHT = 1630
PADDING_HEIGHT_START_OFFSET = 40
PADDING_WIDTH_START_OFFSET = 40
PADDING_HEIGHT_BETWEEN_OFFSET = 10
PADDING_WIDTH_BETWEEN_OFFSET = 5
TEXT_MARGIN = 10
PADDING_HEIGHT_BEFORE_TEXT = 40


PANEL_TYPES_DATA = {
    'L': {
        'name': 'landscape',
        'width': 1024,
        'height': 512
    },
    'C': {
        'name': 'case',
        'width': 512,
        'height': 512
    },
    'P': {
        'name': 'portrait',
        'width': 341,
        'height': 512
    },
    'p': {
        'name': 'smaller landscape',
        'width': 680,
        'height': 512
    }
}
PANEL_TYPES = list(PANEL_TYPES_DATA.keys())
HANDLED_LINES = {
    1: ['P'],
    2: [],
    3: ['L', 'CC', 'PPP']
}

def s(val):
    return int(val * c.upscale_by if c.hr else val)

def generate_pages(page, imgs, batch_size):
    panel_lines = page['panels']
    nb_panels = len(''.join(panel_lines))
    panel_texts = page['texts']

    imgs_batches = [
        [imgs[(i*batch_size)+batch_offset] for i in range(nb_panels)]
        for batch_offset in range(batch_size)
    ]

    return list(zip(*[
        generate_page(panel_lines, panel_texts, imgs_batch)
        for imgs_batch in imgs_batches
    ]))


def generate_page(panel_lines, panel_texts, imgs):
    canvas = Image.new('RGB', (s(PAGE_WIDTH), s(PAGE_HEIGHT)), 'black')
    canvas_no_txt = Image.new('RGB', (s(PAGE_WIDTH), s(PAGE_HEIGHT)), 'black')
    draw = ImageDraw.Draw(canvas)
    panel_index = 0

    width_pos = s(PADDING_WIDTH_START_OFFSET)
    height_pos = s(PADDING_HEIGHT_START_OFFSET)
    for panel_line in panel_lines:
        for panel in panel_line:
            panel_data = PANEL_TYPES_DATA[panel]
            copy_image(canvas, imgs[panel_index], panel_data, width_pos, height_pos)
            copy_image(canvas_no_txt, imgs[panel_index], panel_data, width_pos, height_pos)
            write_text(draw, panel_texts[panel_index], width_pos, height_pos, panel_data)

            panel_index += 1
            width_pos += s(panel_data['width']) + s(PADDING_WIDTH_BETWEEN_OFFSET)

        height_pos += s(panel_data['height']) + s(PADDING_HEIGHT_BETWEEN_OFFSET)
        width_pos = s(PADDING_WIDTH_START_OFFSET)

    return canvas, canvas_no_txt

def copy_image(canvas, img, panel_data, width_pos, height_pos):
    img = img.resize((s(panel_data['width']), s(panel_data['height'])), Image.ANTIALIAS)
    canvas.paste(img, (width_pos, height_pos))

def write_text(draw, text, width_pos, height_pos, panel_data):
    if not text: return
    font = ImageFont.truetype('arial.ttf', 20)
    text_width, text_height = draw.textsize(text, font=font)
    text_width_pos = max(width_pos, int(width_pos+(s(panel_data['width'])/2)) - int(text_width/2))
    text_height_pos = height_pos + s(panel_data['height']) - s(PADDING_HEIGHT_BEFORE_TEXT)

    draw.rectangle(
        [
            (text_width_pos, text_height_pos),
            (text_width + text_width_pos + TEXT_MARGIN, text_height + text_height_pos + TEXT_MARGIN)
        ],
        fill='black'
    )
    draw.text((text_width_pos + 5, text_height_pos + 5), text, fill='white', font=font)
