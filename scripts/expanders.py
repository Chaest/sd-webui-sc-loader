from modules import scripts

from sc_loader.payload.prompt import expand_prompt
from sc_loader import context as c

class ExpanderScript(scripts.Script):
    def title(self):
        return 'Sc Expander'

    def show(self, _):
        return scripts.AlwaysVisible

    def process(self, p):
        original_prompt = p.all_prompts[0]
        original_neg_prompt = p.all_negative_prompts[0]

        p.all_prompts[0] = expand_prompt(p.all_prompts[0])
        p.all_negative_prompts[0] = expand_prompt(p.all_negative_prompts[0])

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params['Original prompt'] = original_prompt
        if original_neg_prompt != p.all_negative_prompts[0]:
            p.extra_generation_params['Original negative prompt'] = original_neg_prompt
