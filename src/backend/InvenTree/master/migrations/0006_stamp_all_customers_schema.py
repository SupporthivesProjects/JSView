from django.db import migrations


class Migration(migrations.Migration):
    """Bring older Stamp tables in line with 0001_initial.

    Squashed 0001 already declares all_customers and customers on Stamp.
    Databases created before that squash never got those columns, and
    Django will not emit a new AddField because state already has them.
    This SQL is idempotent so fresh installs that already have the
    columns/table are unharmed.
    """

    dependencies = [
        ('company', '0082_company_default_stone_rate_company_group_id_and_more'),
        ('master', '0005_alter_metalpurity_karat'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE master_stamp
                    ADD COLUMN IF NOT EXISTS all_customers boolean NOT NULL DEFAULT false;

                    CREATE TABLE IF NOT EXISTS master_stamp_customers (
                        id bigserial PRIMARY KEY,
                        stamp_id bigint NOT NULL REFERENCES master_stamp (id) DEFERRABLE INITIALLY DEFERRED,
                        company_id integer NOT NULL REFERENCES company_company (id) DEFERRABLE INITIALLY DEFERRED
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS master_stamp_customers_stamp_id_company_id_uniq
                        ON master_stamp_customers (stamp_id, company_id);
                    CREATE INDEX IF NOT EXISTS master_stamp_customers_stamp_id_idx
                        ON master_stamp_customers (stamp_id);
                    CREATE INDEX IF NOT EXISTS master_stamp_customers_company_id_idx
                        ON master_stamp_customers (company_id);
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
