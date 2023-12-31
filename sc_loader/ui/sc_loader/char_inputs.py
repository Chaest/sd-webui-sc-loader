import gradio as gr

from ... import context as c

from ..ui_part import UiPart

def get_chars():
    return [
        '--- Lists ---',
        *sorted(list(c.database['series'].get('characters', {}).keys())),
        '--- Characters ---',
        *sorted(list(c.database['prompts']['characters'].keys()))
    ]

class CharInputs(UiPart):
    def build_components(self):
        self.characters = [None] * self.parent.nb_max_chars
        self.prompts = [None] * self.parent.nb_max_chars
        self.character_pickers = [None] * self.parent.nb_max_chars
        self.character_prompts = [None] * self.parent.nb_max_chars
        with gr.Column(scale=80):
            for i in range(self.parent.nb_max_chars):
                with gr.Row(visible=False) as self.character_pickers[i]:
                    self.characters[i] = gr.Dropdown(
                        label=c.database['character_types'][i],
                        choices=get_chars(),
                        type='value'
                    )
                    self.prompts[i] = gr.Textbox(label='')

    def reload_data(self):
        return self.characters, ([lambda: {'choices': get_chars()}] * self.parent.nb_max_chars)

    @property
    def components(self):
        return self.characters, self.prompts, self.character_pickers
