from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from users.models import RuleSet


@receiver(pre_save, sender=User)
def remember_old_username(sender, instance, **kwargs):
    instance._old_username = None
    if instance.pk:
        instance._old_username = (
            User.objects.filter(pk=instance.pk).values_list('username', flat=True).first()
        )


@receiver(post_save, sender=User)
def sync_personal_group(sender, instance, created, update_fields=None, **kwargs):
    if update_fields and set(update_fields) == {'last_login'}:
        return

    old_username = getattr(instance, '_old_username', None)
    if (
        not created
        and old_username
        and old_username != instance.username
        and not Group.objects.filter(name=instance.username).exists()
    ):
        Group.objects.filter(name=old_username).update(name=instance.username)

    def assign_group():
        relation = User.profile.related
        relation.related_model.objects.get_or_create(**{relation.field.name: instance})

        group, group_created = Group.objects.get_or_create(name=instance.username)

        if group_created:
            RuleSet.objects.filter(group=group).update(can_view=True)
            # RuleSet.objects.filter(group=group).exclude(
            #     name__startswith='report'
            # ).update(can_view=True)

        if not instance.groups.filter(pk=group.pk).exists():
            instance.groups.add(group)

    transaction.on_commit(assign_group)


@receiver(post_delete, sender=User)
def delete_personal_group(sender, instance, **kwargs):
    Group.objects.filter(name=instance.username).delete()