from django.db import transaction
from revision.costcard.services import create_cost_card_version


@transaction.atomic
def create_cost_card(cost_card, user=None):
    cost_card.save()

    create_cost_card_version(
        cost_card=cost_card,
        user=user,
    )

    return cost_card


@transaction.atomic
def update_cost_card(cost_card, user=None):
    cost_card.save()

    create_cost_card_version(
        cost_card=cost_card,
        user=user,
    )

    return cost_card