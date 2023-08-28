import re

def normalized_name(name):
    name = re.sub('[^a-z0-9-]', '', name.lower().replace(' ', '-').replace('_', '-'))
    while '--' in name:
        name = name.replace('--', '-')
    if name[-1] == '-':
        name = name[:-1]
    if name[0] == '-':
        name = name[1:]
    return name