import random
from datetime import datetime

from .. import context as c

anti_stack_overflow = ''

def remove(str, olds):
    for old in olds:
        str = str.replace(old, '')
    return str

def expand_prompt(prompt):
    global anti_stack_overflow
    expanders = [word for word in remove(prompt.replace('\n', ' ').replace(',', ' '), '()[]').split(' ') if word and word[0] == '$']
    for expander in expanders:
        expander_value = c.database['prompts'][expander[1:]]
        expanded_value = expander_value if isinstance(expander_value, str) else random.choice(expander_value)
        prompt = prompt.replace(expander, expanded_value)
    if anti_stack_overflow == prompt:
        return prompt
    anti_stack_overflow = prompt
    return expand_prompt(prompt) if '$' in prompt else prompt

def build_prompts(scenario, characters):
    build_short_prompt(scenario)
    chars_prompts = []
    chars_neg_prompts = []
    for i in range(len(scenario['characters'])):
        character_type = scenario['characters'][i]
        sc_char_prompt = scenario['prompts'][character_type]
        db_char_prompt = c.database['prompts']['characters'][characters[i]]
        if isinstance(db_char_prompt, list):
            chars_neg_prompts.append(db_char_prompt[1])
            db_char_prompt = db_char_prompt[0]
        chars_prompts.append(','.join((sc_char_prompt['pre'], db_char_prompt, sc_char_prompt['post'])))

    positive_prompt = '\n'.join((
        scenario['prompts']['quality'],
        scenario['prompts']['general'],
        c.positive or ''
    ))
    positive_prompt = ' AND '.join([positive_prompt, *chars_prompts])
    negative_prompt = scenario['prompts']['negative'] + ',' + (c.negative or '') + ',' + ','.join(chars_neg_prompts)

    return {
        'prompt': expand_prompt(positive_prompt),
        'negative_prompt': expand_prompt(negative_prompt)
    }

def build_short_prompt(scenario):
    positive_prompt = '\n'.join((
        f'[[Scenario Loader v{c.version}]]',
        '## ' + datetime.today().strftime('%Y-%m-%d'),
        scenario['prompts']['quality'] + ', ' + (c.positive or ''),
        f'scenario: {c.scenario}',
        '\n'.join([f'@{c.chars[idx]}' for idx, _ in enumerate(scenario['characters'])])
    ))
    negative_prompt = scenario['prompts']['negative'] + ', ' + (c.negative or '')

    c.short_prompts = {
        'positive': positive_prompt,
        'negative': negative_prompt
    }
