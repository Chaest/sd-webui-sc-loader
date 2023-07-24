class UiPart:
    def __init__(self, parent):
        self.parent = parent

    def build_components(self):
        pass

    def link_actions(self):
        pass

    @property
    def components(self):
        pass

    def reload_data(self):
        return [], []

    def build(self):
        self.build_components()
        self.link_actions()
        return self.components
