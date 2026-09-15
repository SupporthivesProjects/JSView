import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('purchase_order', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='prepby',
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='prepby',
            field=models.ForeignKey(
                blank=True,
                help_text='InvenTree user who created this purchase request or order.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='prepared_purchase_orders',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Prepared By',
            ),
        ),
        migrations.AddIndex(
            model_name='purchaseorder',
            index=models.Index(fields=['prepby'], name='purchase_or_prepby_idx'),
        ),
    ]
