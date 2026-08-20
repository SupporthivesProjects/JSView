import os

from django.core.files.base import ContentFile
from django.db import transaction

from .models import (
    CostCard,
    CostCardDiamondLine,
    CostCardColorStoneLine,
    CostCardFinishLine,
)


def copy_file(file_field):
    if not file_field:
        return None

    file_field.open("rb")
    content = file_field.read()
    file_field.close()

    return ContentFile(
        content,
        name=os.path.basename(file_field.name),
    )


def copy_fields(source, target, excluded_fields):
    file_fields = {
        field.name
        for field in source._meta.fields
        if field.__class__.__name__ in {"FileField", "ImageField"}
    }

    for field in source._meta.fields:
        if field.name in excluded_fields:
            continue

        value = getattr(source, field.name)

        if field.name in file_fields:
            if value:
                setattr(target, field.name, copy_file(value))
        else:
            setattr(target, field.name, value)


@transaction.atomic
def duplicate_cost_card(cost_card):
    original = cost_card

    new_card = CostCard()

    copy_fields(
        original,
        new_card,
        {
            "id",
            "cost_card_no",
            "parent",
            "created_at",
            "updated_at",
        },
    )

    new_card.parent = original
    new_card.cost_card_no = None
    new_card.save()

    for original_line in original.diamond_lines.all():
        new_line = CostCardDiamondLine()

        copy_fields(
            original_line,
            new_line,
            {
                "id",
                "cost_card",
                "created_at",
                "updated_at",
            },
        )

        new_line.cost_card = new_card
        new_line.save()

    for original_line in original.colorstone_lines.all():
        new_line = CostCardColorStoneLine()

        copy_fields(
            original_line,
            new_line,
            {
                "id",
                "cost_card",
                "created_at",
                "updated_at",
            },
        )

        new_line.cost_card = new_card
        new_line.save()

    for original_line in original.finish_lines.all():
        new_line = CostCardFinishLine()

        copy_fields(
            original_line,
            new_line,
            {
                "id",
                "cost_card",
                "created_at",
                "updated_at",
            },
        )

        new_line.cost_card = new_card
        new_line.save()

    return new_card