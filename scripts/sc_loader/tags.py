import re

from . import context as c

def update_tags(tags):
    if c.tags is None:
        c.tags = []
    for tag in tags:
        if tag not in c.tags: # don't use set trick to keep order
            c.tags.append(tag)

def cli_tags(args):
    return args.tags.split(',') if args.tags else []
