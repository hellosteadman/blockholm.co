import json
import os


EMBED_PROVIDERS = json.load(
    open(
        os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'providers.json'
        ),
        'rb'
    )
)

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) '
    'Version/17.5 Safari/605.1.15'
)
