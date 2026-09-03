from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_rate_customers'),
    ]

    operations = [
        migrations.AddField(
            model_name='colorstonesize',
            name='sieve_size',
            field=models.CharField(
                blank=True,
                help_text='Sieve size corresponding to this color stone size.',
                max_length=50,
                null=True,
                verbose_name='Sieve Size',
            ),
        ),
    ]
