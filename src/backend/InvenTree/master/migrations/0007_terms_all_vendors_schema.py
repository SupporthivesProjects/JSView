from django.db import migrations


class Migration(migrations.Migration):
    """Bring older Terms tables in line with 0001_initial.

    Same squash gap as Stamp: all_vendors / vendors M2M exist in state
    but not on databases created before the master 0001 rewrite.
    SQL is idempotent for fresh installs.
    """

    dependencies = [
        ('company', '0082_company_default_stone_rate_company_group_id_and_more'),
        ('master', '0006_stamp_all_customers_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE master_terms
                    ADD COLUMN IF NOT EXISTS all_vendors boolean NOT NULL DEFAULT false;

                    CREATE TABLE IF NOT EXISTS master_terms_vendors (
                        id bigserial PRIMARY KEY,
                        terms_id bigint NOT NULL REFERENCES master_terms (id) DEFERRABLE INITIALLY DEFERRED,
                        company_id integer NOT NULL REFERENCES company_company (id) DEFERRABLE INITIALLY DEFERRED
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS master_terms_vendors_terms_id_company_id_uniq
                        ON master_terms_vendors (terms_id, company_id);
                    CREATE INDEX IF NOT EXISTS master_terms_vendors_terms_id_idx
                        ON master_terms_vendors (terms_id);
                    CREATE INDEX IF NOT EXISTS master_terms_vendors_company_id_idx
                        ON master_terms_vendors (company_id);
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
