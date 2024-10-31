from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class BlockQuerySet(QuerySet):
    def render(self, simple=False):
        blocks = []
        in_list = None
        list_items = []

        for block in self.all():
            if block.type == 'bulleted_list_item':
                if not in_list:
                    in_list = 'bulleted'

                list_items.append(block.properties)
            else:
                if in_list:
                    if simple:
                        blocks.append(
                            render_to_string(
                                'notion/content/bulleted_list_block.html',
                                {
                                    'items': list_items,
                                    'simple': True
                                }
                            )
                        )
                    else:
                        blocks.append(
                            '<div class="%s-list-block">%s</div>' % (
                                in_list,
                                render_to_string(
                                    'notion/content/bulleted_list_block.html',
                                    {
                                        'items': list_items,
                                        'simple': False
                                    }
                                )
                            )
                        )

                    in_list = None
                    list_items = []

                if simple:
                    blocks.append(
                        block.render(simple)
                    )
                else:
                    blocks.append(
                        '<div class="%s-block">%s</div>' % (
                            block.type.replace('_', '-'),
                            block.render(simple)
                        )
                    )

        if in_list:
            if simple:
                blocks.append(
                    render_to_string(
                        'notion/content/bulleted_list_block.html',
                        {
                            'items': list_items,
                            'simple': True
                        }
                    )
                )
            else:
                blocks.append(
                    '<div class="%s-list-block">%s</div>' % (
                        in_list,
                        render_to_string(
                            'notion/content/bulleted_list_block.html',
                            {
                                'items': list_items,
                                'simple': False
                            }
                        )
                    )
                )

        return mark_safe(''.join(blocks))
