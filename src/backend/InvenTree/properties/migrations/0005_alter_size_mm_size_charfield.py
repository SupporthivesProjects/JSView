from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_colorstonesize_sieve_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diamondsize',
            name='mm_size',
            field=models.CharField(
                blank=True,
                help_text='Diamond size in millimeters.',
                max_length=50,
                null=True,
                verbose_name='Size (mm)',
            ),
        ),
        migrations.AlterField(
            model_name='colorstonesize',
            name='mm_size',
            field=models.CharField(
                blank=True,
                help_text='Color stone size in millimeters.',
                max_length=50,
                null=True,
                verbose_name='Size (mm)',
            ),
        ),
    ]
