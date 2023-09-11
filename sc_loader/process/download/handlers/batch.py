from ..db import get_batches_path
from .model import handle_model
from .mono import generic_handler

def handle_batch(batch_name):
    return process_batch(get_batches_path(batch_name))

def process_batch(batch_path):
    with open(batch_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    batch_elements = []
    batch_idx = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('> '):
            if batch_idx-1 >= 0:
                batch_elements[batch_idx-1].append(line[2:])
        else:
            batch_idx += 1
            batch_elements.append([line])

    batches_results = ''
    for batch_element in batch_elements:
        try:
            msg = batch_line_handler(*batch_element)
            if msg.startswith('ERROR'):
                msg = msg.replace('<br>', '\n').strip().split('\n')[-1]
                batches_results += f'Failed ({msg})\n'
            elif msg.startswith('IGNORED'):
                batches_results += 'Ignored\n'
            else:
                batches_results += 'Success\n'
        except Exception as e:
            batches_results += f'Failed ({e})\n'

    update_batch_file(batch_path, batch_elements, batches_results)

    return batches_results.replace('\n', '<br>')

def update_batch_file(batch_path, batch_elements, batches_results):
    results = batches_results.strip().split('\n')
    with open(batch_path, 'w', encoding='utf-8') as f:
        for idx, result in enumerate(results):
            prefix = '* ' if result == 'Success' else ''
            f.write(prefix + batch_elements[idx][0] + '\n')
            for subline in batch_elements[idx][1:]:
                f.write('> ' + subline + '\n')


def batch_line_handler(batch_line, batch_pos_line=None, batch_neg_line=None):
    if batch_line[0][0] == '*': return 'IGNORED'
    while '  ' in batch_line: batch_line = batch_line.replace('  ', ' ')
    elements = batch_line.split(' ')
    if len(elements) == 1:
        return generic_handler(elements[0])
    prompt_type, sc_file = elements[1].split('/')

    weight = 0.75
    name = '_'
    if len(elements) > 2:
        try:
            weight = float(elements[2])
        except:
            name = elements[2]
    if len(elements) > 3:
        try:
            weight = float(elements[3])
        except:
            if name != '_':
                raise Exception(f'Invalid batch line {batch_line}')
            name = elements[3]

    return handle_model(sc_file, name, elements[0], batch_pos_line or '', batch_neg_line or '', weight, prompt_type)
