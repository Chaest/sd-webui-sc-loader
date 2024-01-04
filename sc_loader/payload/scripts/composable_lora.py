import re

from modules.shared import opts

from ... import context as c

COMP_OPTS = {
      'decrease': {
            'name': 'decrease [LORA #decrease]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>\s+#decrease\].*',
            'from': lambda lora: f'[{lora} #decrease]'
      },
      'increase': {
            'name': 'increment [LORA #increment]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>\s+#increment\].*',
            'from': lambda lora: f'[{lora} #increment]'
      },
      'e10': {
            'name': 'until 10 [LORA::10]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>::10\].*',
            'from': lambda lora: f'[{lora}::10]'
      },
      's10': {
            'name': 'from 10 [LORA:10]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>:10\].*',
            'from': lambda lora: f'[{lora}:10]'
      },
      '50%': {
            'name': '50% steps [LORA:0.5]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>:0.5\].*',
            'from': lambda lora: f'[{lora}:0.5]]'
      },
      '10_25': {
            'name': '10 to 25 [[LORA::25]:10]',
            'rgxp': r'.*\[\[<(?:lora|lyco):([^:]+):([^>]+)>::25\]:10\].*',
            'from': lambda lora: f'[[{lora}::25]:10]'
      },
      'increase_s10': {
            'name': 'increment from 10 [LORA #increment:10]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>\s+#increment:10\].*',
            'from': lambda lora: f'[{lora} #increment:10]'
      },
      'decrease_s10': {
            'name': 'decrease from 10 [LORA #decrease:10]',
            'rgxp': r'.*\[<(?:lora|lyco):([^:]+):([^>]+)>\s+#decrease:10\].*',
            'from': lambda lora: f'[{lora} #decrease:10]'
      },
}
ALL_REGEX = r'(.*)\[?<(lora|lyco):([^:]+):(?:[^>]+)>(?:.+\])?(.*)'

def adapt_lora(prompt, i):
    if not opts.sc_loader_enable_lora_options: return prompt
    m = re.match(ALL_REGEX, prompt)
    if not m: return prompt
    pre = m[1]
    type_ = m[2]
    name = m[3]
    post = m[4]
    weight = c.char_weights[i]
    operation = c.char_comopts[i]
    lora = COMP_OPTS.get(operation, {'from':lambda x: x})['from'](f'<{type_}:{name}:{weight}>')
    return f'{pre}{lora}{post}'
