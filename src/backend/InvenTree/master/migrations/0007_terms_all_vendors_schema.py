from django.db import migrations


def apply_terms_vendors_schema(apps, schema_editor):
    """Run the idempotent Postgres DDL only when on PostgreSQL.

    Same squash gap as Stamp: all_vendors / vendors M2M exist in state
    but not on databases created before the master 0001 rewrite.
    SQLite doesn't support `ADD COLUMN IF NOT EXISTS`, `bigserial`,
    or `DEFERRABLE`, and doesn't need this fix-up anyway since fresh
    SQLite databases are created directly from the current model state.
    """
    if schema_editor.connection.vendor != 'postgresql':
        return

    schema_editor.execute(
        """
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
        """
    )


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """Bring older Terms tables in line with 0001_initial.

    Same squash gap as Stamp: all_vendors / vendors M2M exist in state
    but not on databases created before the master 0001 rewrite.
    SQL is idempotent for fresh installs. Only runs on PostgreSQL;
    SQLite databases already have the correct schema from initial
    migration.
    """

    dependencies = [
        ('company', '0082_company_default_stone_rate_company_group_id_and_more'),
        ('master', '0006_stamp_all_customers_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunPython(
                    apply_terms_vendors_schema,
                    reverse_noop,
                ),
            ],
        ),
    ]
