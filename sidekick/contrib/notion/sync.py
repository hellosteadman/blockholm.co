from django.apps import apps
from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Model as DjangoModel
from django.db.models.fields.related import RelatedField
from notion_client import Client
from notion_client.helpers import iterate_paginated_api
from . import settings
from .blocks import Block
from .properties import Property
import json


def to_model(Model, before_clean=None, blocks_field=None, media_handler=''):
    users = {}

    def get_properties(doc):
        returned = {}
        for name, attrs in result['properties'].items():
            returned[name] = Property(name, attrs)

        return returned

    def get_user(definition):
        notion_id = definition['id']
        
        if notion_id in users:
            return users[notion_id]

        response = notion.users.retrieve(notion_id)
        email = response['person']['email']

        if user := User.objects.get(email=email):
            users[notion_id] = user
            return user

        raise Exception('%(name)s could not be found' % result)

    def get_blocks(doc, obj):
        returned = {}
        block_response = notion.blocks.children.list(doc['id'])
        kwargs = {}

        if media_handler:
            kwargs['handle_media'] = getattr(obj, media_handler)

        for result in block_response.get('results', []):
            returned[result['id']] = Block(result, **kwargs)

        return returned

    def has_field(name):
        try:
            Model._meta.get_field(name)
            return True
        except FieldDoesNotExist:
            return False

    notion = Client(auth=settings.API_KEY)
    for dbname, dbid in settings.DATABASES.items():
        if not issubclass(apps.get_model(dbname), Model):
            continue

        try:
            obj_blocks_field = Model._meta.get_field(blocks_field)
        except FieldDoesNotExist:
            obj_blocks_field = None
            blocks_parent = None
            BlockModel = None
        else:
            blocks_parent = obj_blocks_field.remote_field.name
            BlockModel = obj_blocks_field.related_model

        pks = []
        response = iterate_paginated_api(
            notion.databases.query,
            database_id=dbid
        )

        for result in response:
            with transaction.atomic():
                objid = result['id']
                obj = Model.objects.select_for_update().filter(
                    notion_id=objid
                ).first() or Model(
                    notion_id=objid
                )

                after = {}

                for pname, prop in get_properties(result).items():
                    try:
                        prop_value = prop.to_python()
                    except NotImplementedError:
                        raise Exception(prop)

                    if prop.type == 'title' and has_field('title'):
                        obj.title = prop_value
                    else:
                        fname = prop.name.replace(' ', '_').lower()

                        try:
                            field = Model._meta.get_field(fname)
                        except FieldDoesNotExist:
                            continue
                        else:
                            if isinstance(field, RelatedField):
                                after[field.name] = (field, prop_value)
                            else:
                                setattr(obj, field.name, prop_value)

                if has_field('author'):
                    obj.author = get_user(result['created_by'])

                if callable(before_clean):
                    before_clean(obj, result)

                obj.full_clean()
                obj.save()
                pks.append(obj.pk)

                for fname, (field, value) in after.items():
                    related_manager = getattr(obj, fname)
                    added_rels = []
                    Related = field.related_model

                    for item in value:
                        if isinstance(item, str):
                            robj, _ = Related.objects.get_or_create(
                                name=item
                            )
                        elif isinstance(item, DjangoModel):
                            robj = item
                        else:
                            raise Exception(item)

                        added_rels.append(robj)
                    
                    related_manager.add(*added_rels)
                    related_manager.remove(
                        *related_manager.exclude(
                            pk__in=[r.pk for r in added_rels]
                        )
                    )

                if obj_blocks_field is None:
                    continue

                obj_blocks = getattr(obj, obj_blocks_field.name)
                block_ids = []

                for i, (block_id, block) in enumerate(
                    get_blocks(result, obj).items()
                ):
                    obj_block = obj_blocks.filter(
                        notion_id=block_id
                    ).first() or BlockModel(
                        **{
                            blocks_parent: obj
                        },
                        notion_id=block_id
                    )

                    obj_block.type = block.type
                    obj_block.ordering = i

                    try:
                        obj_block.properties = block.to_python()
                    except Exception as ex:
                        print(json.dumps(block._definition, indent=4))
                        raise Exception('Confused by blcok definition') from ex

                    obj_block.full_clean()
                    obj_block.save()
                    block_ids.append(obj_block.pk)

                obj_blocks.exclude(pk__in=block_ids).delete()

        Model.objects.exclude(pk__in=pks).delete()
        return Model.objects.filter(pk__in=pks)


def from_model(obj):
    for dbname, dbid in settings.DATABASES.items():
        Model = apps.get_model(dbname)

        if not isinstance(obj, Model):
            continue

        notion = Client(auth=settings.API_KEY)
        response = notion.databases.retrieve(dbid)
        attrs = {}

        for name, definition in response['properties'].items():
            prop = Property(name, definition)
            field_name = name.replace(' ', '_').lower()

            try:
                dbfield = Model._meta.get_field(field_name)
            except FieldDoesNotExist:
                continue

            value = getattr(obj, dbfield.name)
            if isinstance(dbfield, RelatedField):
                value = value.all()    

            if value is not None:
                attrs[definition['id']] = prop.from_python(value)

        if obj.notion_id:
            notion.pages.update(
                str(obj.notion_id),
                properties=attrs
            )

            return obj.notion_id
        else:
            doc = notion.pages.create(
                parent={
                    'database_id': dbid
                },
                properties=attrs
            )

        return doc['id']
