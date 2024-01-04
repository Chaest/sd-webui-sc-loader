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

        expanded_prompt = expand_prompt(p.all_prompts[0])
        expanded_neg_prompt = expand_prompt(p.all_negative_prompts[0])

        p.all_prompts = [expanded_prompt for prompt in p.all_prompts]
        p.all_negative_prompts = [expanded_neg_prompt for prompt in p.all_negative_prompts]

        if original_prompt != p.all_prompts[0]:
            p.extra_generation_params['Original prompt'] = original_prompt
        if original_neg_prompt != p.all_negative_prompts[0]:
            p.extra_generation_params['Original negative prompt'] = original_neg_prompt
