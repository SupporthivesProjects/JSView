from datetime import date, datetime
from decimal import Decimal

from django.db import transaction
from django.db.models.fields.files import FieldFile

from revision.models import CostCardVersion


def serialize_value(value):
    if isinstance(value, FieldFile):
        if not value:
            return None

        return {
            'name': value.name,
            'url': value.url,
        }

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def serialize_model(instance):
    data = {
        'id': instance.pk,
    }

    for field in instance._meta.concrete_fields:
        if field.name == 'id':
            continue

        value = getattr(instance, field.name, None)

        if field.is_relation:
            data[field.name] = value.pk if value else None
        else:
            data[field.name] = serialize_value(value)

    for field in instance._meta.many_to_many:
        data[field.name] = [
            item.pk
            for item in getattr(instance, field.name).all()
        ]

    return data


def build_cost_card_snapshot(cost_card):
    snapshot = {
        'cost_card': serialize_model(cost_card),
    }

    for relation in cost_card._meta.related_objects:
        if not relation.auto_created or not relation.one_to_many:
            continue

        accessor_name = relation.get_accessor_name()

        if accessor_name in {'child_cards', 'versions'}:
            continue

        manager = getattr(cost_card, accessor_name, None)

        if manager is None:
            continue

        snapshot[accessor_name] = [
            serialize_model(instance)
            for instance in manager.all()
        ]

    return snapshot


@transaction.atomic
def create_cost_card_version(cost_card, user=None):
    cost_card_model = cost_card.__class__

    cost_card = (
        cost_card_model.objects
        .select_for_update()
        .get(pk=cost_card.pk)
    )

    last_version = (
        CostCardVersion.objects
        .filter(cost_card=cost_card)
        .order_by('-version')
        .first()
    )

    version = 1 if last_version is None else last_version.version + 1

    return CostCardVersion.objects.create(
        cost_card=cost_card,
        version=version,
        created_by=user,
        data=build_cost_card_snapshot(cost_card),
        active=True,
    )