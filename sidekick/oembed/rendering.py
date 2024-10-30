class RendererBase(object):
    def __init__(self, domain):
        self.domain = domain

    def render(self, path):
        raise NotImplementedError('Method not implemented')
