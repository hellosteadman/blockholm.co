from collections import defaultdict
from urllib.parse import urlparse


class Library(object):
    def __init__(self):
        self.__registry = defaultdict(list)

    def register(self, domain, renderer):
        self.__registry[domain].append(
            renderer(domain)
        )

    def render_for_url(self, url):
        urlparts = urlparse(url)
        domain = urlparts.hostname

        while domain.startswith('www.'):
            domain = domain[4:]

        for renderer in self.__registry[domain]:
            rendered = renderer.render(urlparts.path)
            if rendered is not None:
                return rendered
