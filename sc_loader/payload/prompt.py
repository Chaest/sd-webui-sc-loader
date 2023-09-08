import random

from .. import context as c

anti_stack_overflow = ''

def expand_prompt(prompt):
    global anti_stack_overflow
    for expander in get_expanders(prompt):
        prompt = prompt.replace(expander, get_expander_value(expander))
    if anti_stack_overflow == prompt:
        return prompt
    anti_stack_overflow = prompt
    return expand_prompt(prompt) if '$' in prompt else prompt

def build_prompts(scenario, characters):
    chars_prompts = []
    chars_neg_prompts = []
    for i in range(len(scenario['characters'])):
        character_type = scenario['characters'][i]
        sc_char_prompt = scenario['prompts'][character_type]
        db_char_prompt = c.database['prompts']['characters'][characters[i]]
        if isinstance(db_char_prompt, list):
            chars_neg_prompts.append(db_char_prompt[1])
            db_char_prompt = db_char_prompt[0]
        chars_prompts.append(','.join((sc_char_prompt['pre'], db_char_prompt, c.char_prompts[i], sc_char_prompt['post'])))

    positive_prompt = '\n'.join((
        scenario['prompts']['quality'],
        scenario['prompts']['general'],
        c.positive or ''
    ))
    positive_prompt = ' AND '.join([positive_prompt, *chars_prompts]) if len(chars_prompts) != 1 else positive_prompt + ', ' + chars_prompts[0]
    negative_prompt = scenario['prompts']['negative'] + ',' + (c.negative or '') + ',' + ','.join(chars_neg_prompts)

    return {
        'prompt': expand_prompt(positive_prompt),
        'negative_prompt': expand_prompt(negative_prompt)
    }

def remove(str_, olds):
    for old in olds:
        str_ = str_.replace(old, '')
    return str_

def get_expanders(prompt):
    prompt = prompt.replace('\n', ' ').replace(',', ' ').replace('$$', '')
    prompt = remove(prompt, '()[]')
    return [word for word in prompt.split(' ') if word and word[0] == '$']

def get_expander_value(expander):
    expander_name = expander[1:]
    if '.' not in expander_name:
        expander_value = c.database['prompts'][expander[1:]]
        expander_value = expander_value if isinstance(expander_value, str) else random.choice(expander_value)
    else:
        expander_path = expander_name.split('.')
        expander_value = c.database['prompts'][expander_path[0]]
        for expander_path_part in expander_path[1:]:
            expander_value = process_path(expander_value, expander_path_part)
        expander_value = expander_value if isinstance(expander_value, str) else random.choice(expander_value)
    return expander_value

def process_path(expander_value, expander_next_name):
    try:
        expander_next_name = int(expander_next_name)
    except: pass
    return expander_value[expander_next_name]
