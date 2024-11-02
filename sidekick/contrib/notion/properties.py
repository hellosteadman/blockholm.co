from dateutil.parser import parse as parse_date
from django.apps import apps
from . import settings


class PropertyBase(object):
    def __init__(self, name, definition):
        self.name = name
        self.type = definition['type']
        self.value = definition[self.type]
        self._definition = definition

    def to_python(self):
        return self.value

    def from_python(self, value):
        return {
            self.type: value
        }


class DateProperty(PropertyBase):
    def to_python(self):
        if self.value is None:
            return None

        if not isinstance(self.value, dict):
            raise Exception(
                '\'%s\' should be a dict' % self.type,
                self._definition
            )

        start = self.value['start']
        return parse_date(start)


class UrlProperty(PropertyBase):
    pass


class SelectProperty(PropertyBase):
    def to_python(self):
        if self.value is None:
            return None

        return self.value['name']

    def from_python(self, value):
        return {
            self.type: {
                'name': str(value)
            }
        }


class MultiSelectProperty(PropertyBase):
    def to_python(self):
        names = []
        for item in self.value:
            names.append(item['name'])

        return list(sorted(names))

    def from_python(self, value):
        return {
            self.type: [
                {
                    'name': str(v)
                } for v in value
            ]
        }


class StatusProperty(SelectProperty):
    pass


class TextProperty(PropertyBase):
    def to_python(self):
        returned = ''
        for part in self.value:
            text = part['plain_text']
            returned += text

        return returned

    def from_python(self, value):
        return {
            self.type: [
                {
                    'type': 'text',
                    'text': {
                        'content': value
                    }
                }
            ]
        }


class TitleProperty(TextProperty):
    pass


class RichTextProperty(TextProperty):
    pass


class EmailProperty(PropertyBase):
    pass


class CheckboxProperty(PropertyBase):
    pass


class RelationProperty(PropertyBase):
    def to_python(self):
        items = []

        for dbname, dbid in settings.DATABASES.items():
            Model = apps.get_model(dbname)
            items.extend(
                Model.objects.filter(
                    notion_id__in=[
                        item['id'] for item in self.value
                    ]
                ).distinct()
            )

        return set(items)

    def from_python(self, value):
        return {
            self.type: [
                hasattr(v, 'notion_id') and {
                    'id': str(v.notion_id)
                } or {
                    'name': str(v)
                }
                for v in value
            ]
        }


def Property(name, definition):
    prop_type = definition['type']

    try:
        prop_cls = {
            'date': DateProperty,
            'url': UrlProperty,
            'title': TitleProperty,
            'rich_text': RichTextProperty,
            'select': SelectProperty,
            'multi_select': MultiSelectProperty,
            'status': StatusProperty,
            'text': TextProperty,
            'email': EmailProperty,
            'checkbox': CheckboxProperty,
            'relation': RelationProperty
        }[prop_type]

        return prop_cls(name, definition)
    except KeyError:
        raise Exception('Unsupported property type', prop_type)
