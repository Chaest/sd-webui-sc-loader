import gradio as gr

from ... import context as c

from ..ui_part import UiPart

class CharInputs(UiPart):
    def get_chars(self):
        return [
        '--- Lists ---',
        *list(c.database['series']['characters'].keys()),
        '--- Scenarios ---',
        *list(c.database['prompts']['characters'].keys())
    ]

    def build_components(self):
        self.characters = [None] * self.parent.nb_max_chars
        self.character_rows = [None] * self.parent.nb_max_chars
        with gr.Column(scale=80):
            for i in range(self.parent.nb_max_chars):
                with gr.Row(visible=False) as self.character_rows[i]:
                    self.characters[i] = gr.Dropdown(
                        label=c.database['character_types'][i],
                        choices=self.get_chars(),
                        type='value'
                    )

    def reload_data(self):
        return self.characters, ([lambda: {'choices': self.get_chars()}] * self.parent.nb_max_chars)

    @property
    def components(self):
        return self.characters, self.character_rows
