from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class BlockQuerySet(QuerySet):
    def render(self):
        blocks = []
        in_list = 'bulleted'
        list_items = []

        for block in self.all():
            if block.type == 'bulleted_list_item':
                if not in_list:
                    in_list = 'bulleted'

                list_items.append(block.properties)
            else:
                if in_list:
                    blocks.append(
                        '<div class="%s-list-block">%s</div>' % (
                            in_list,
                            render_to_string(
                                'newsletter/content/bulleted_list_block.html',
                                {
                                    'items': list_items
                                }
                            )
                        )
                    )

                    in_list = None

                blocks.append(
                    '<div class="%s-block">%s</div>' % (
                        block.type.replace('_', '-'),
                        block.render()
                    )
                )

        return mark_safe(''.join(blocks))
