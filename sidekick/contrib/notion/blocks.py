from notion_client import Client
from . import settings


class BlockBase(object):
    def __init__(self, definition, handlers={}):
        self.type = definition['type']
        self.value = definition[self.type]
        self._definition = definition

        for key, func in handlers.items():
            setattr(self, 'handle_%s' % key, func)

    def get_children(self):
        if self._definition['has_children']:
            notion = Client(auth=settings.API_KEY)
            response = notion.blocks.children.list(
                self._definition['id']
            )

            kwargs = {
                'handle_media': getattr(self, 'handle_media', None)
            }

            for result in response.get('results', []):
                yield Block(result, **kwargs)

    def handle_media(self, url):
        raise NotImplementedError

    def to_python(self):
        raise NotImplementedError


class RichTextBlock(BlockBase):
    def to_python(self, value=None):
        returned = ''

        if value is None:
            value = self.value['rich_text']

        for part in value:
            text = part['text']
            annotations = part['annotations']
            content = text['content']

            if annotations.get('code'):
                content = '`%s`' % content
            else:
                if annotations.get('italic'):
                    content = '*%s*' % content

                if annotations.get('bold'):
                    content = '**%s**' % content

            if link := text.get('link'):
                content = '[%s](%s)' % (
                    content,
                    link['url']
                )

            returned += content

        return {
            'text': returned,
            'children': [
                child.to_python()
                for child in self.get_children()
            ]
        }


class ParagraphBlock(RichTextBlock):
    pass


class HeadingBlock(RichTextBlock):
    tag = ''


class Heading1Block(RichTextBlock):
    tag = 'h1'


class Heading2Block(RichTextBlock):
    tag = 'h2'


class Heading3Block(RichTextBlock):
    tag = 'h3'


class ImageBlock(BlockBase):
    def to_python(self):
        return {
            'alt': self.value['caption'],
            'src': self.handle_media(
                self.value['file']['url']
            )
        }


class BulletedListItemBlock(RichTextBlock):
    pass


class QuoteBlock(RichTextBlock):
    pass


class CalloutBlock(RichTextBlock):
    def to_python(self):
        icon, emoji, kind = None, None, 'info'

        if self.value.get('icon'):
            if self.value['icon']['type'] == 'emoji':
                emoji = self.value['icon']['emoji']
            else:
                raise Exception(self.value['icon'])

        if self.value.get('color'):
            kind = {
                'blue_background': 'info',
                'brown_background': 'warning',
                'gray_background': 'light',
                'green_background': 'success',
                'orange_background': 'warning',
                'pink_background': 'info',
                'purple_background': 'warning',
                'red_background': 'danger',
                'yellow_background': 'warning'
            }.get(self.value['color'])

        return {
            'kind': kind,
            'icon': icon,
            'emoji': emoji,
            **super().to_python()
        }


class VideoBlock(BlockBase):
    def to_python(self):
        if self.value['type'] == 'external':
            path = self.value['external']['url']
        else:
            path = self.handle_media(
                self.value['file']['url']
            )

        return {
            'src': path
        }


class DividerBlock(BlockBase):
    def to_python(self):
        return {}


def Block(definition, handle_media=None):
    block_type = definition['type']

    try:
        Block = {
            'paragraph': ParagraphBlock,
            'image': ImageBlock,
            'heading_1': Heading1Block,
            'heading_2': Heading2Block,
            'heading_3': Heading3Block,
            'bulleted_list_item': BulletedListItemBlock,
            'quote': QuoteBlock,
            'video': VideoBlock,
            'divider': DividerBlock,
            'callout': CalloutBlock
        }[block_type]
    except KeyError:
        raise Exception('Unsupported block type', block_type)

    handlers = {}
    if handle_media is not None:
        handlers['media'] = handle_media

    return Block(
        definition,
        handlers=handlers
    )
