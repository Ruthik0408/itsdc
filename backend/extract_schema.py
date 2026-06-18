import psycopg2
from pathlib import Path

from db_config import get_database_settings
from table_exclusions import EXCLUDED_TABLES, get_allowed_source_tables


BACKEND_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BACKEND_DIR / "tulip2.0_schema.md"


def extract_database_schema():
    excluded_tables = sorted(EXCLUDED_TABLES)
    allowed_tables = sorted(get_allowed_source_tables())
    print("⏳ Extracting layout rules from tulip2...")
    print(f"Using only LLAMA_BUSINESS_PRIORITY_TABLES: {', '.join(allowed_tables)}")
    print(f"Skipping excluded tables: {', '.join(excluded_tables)}")
    if not allowed_tables:
        raise RuntimeError("LLAMA_BUSINESS_PRIORITY_TABLES did not provide any usable table names.")
    conn = psycopg2.connect(**get_database_settings())
    cur = conn.cursor()
    cur.execute("SET statement_timeout = '30s';")

    metadata_query = """
    WITH root_tables AS (
        SELECT c.oid, c.relname
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
            AND c.relkind IN ('r', 'p')
            AND c.relname = ANY(%s)
            AND c.relname <> ALL(%s)
    ),
    related_tables AS (
        SELECT DISTINCT ref_cls.oid, ref_cls.relname
        FROM pg_catalog.pg_constraint con
        JOIN root_tables root ON root.oid = con.conrelid
        JOIN pg_catalog.pg_class ref_cls ON ref_cls.oid = con.confrelid
        WHERE con.contype = 'f'
        UNION
        SELECT DISTINCT child_cls.oid, child_cls.relname
        FROM pg_catalog.pg_constraint con
        JOIN root_tables root ON root.oid = con.confrelid
        JOIN pg_catalog.pg_class child_cls ON child_cls.oid = con.conrelid
        WHERE con.contype = 'f'
    ),
    visible_tables AS (
        SELECT oid, relname FROM root_tables
        UNION
        SELECT oid, relname FROM related_tables
    )
    SELECT 
        cls.relname AS table_name,
        attr.attname AS column_name,
        pg_catalog.format_type(attr.atttypid, attr.atttypmod) AS data_type,
        CASE WHEN pk.attnum IS NOT NULL THEN attr.attname END AS is_pk,
        fk.references_table
    FROM pg_catalog.pg_class cls
    JOIN pg_catalog.pg_namespace ns ON ns.oid = cls.relnamespace
    JOIN pg_catalog.pg_attribute attr ON attr.attrelid = cls.oid
    LEFT JOIN LATERAL (
        SELECT attr.attnum
        FROM pg_catalog.pg_index idx
        WHERE idx.indrelid = cls.oid
            AND idx.indisprimary
            AND attr.attnum = ANY(idx.indkey)
        LIMIT 1
    ) pk ON TRUE
    LEFT JOIN LATERAL (
        SELECT ref_cls.relname AS references_table
        FROM pg_catalog.pg_constraint con
        JOIN pg_catalog.pg_class ref_cls ON ref_cls.oid = con.confrelid
        WHERE con.conrelid = cls.oid
            AND con.contype = 'f'
            AND attr.attnum = ANY(con.conkey)
        LIMIT 1
    ) fk ON TRUE
	    WHERE ns.nspname = 'public'
	        AND cls.relkind IN ('r', 'p')
	        AND cls.oid IN (SELECT oid FROM visible_tables)
	        AND cls.relname <> ALL(%s)
	        AND attr.attnum > 0
	        AND NOT attr.attisdropped
	    ORDER BY cls.relname, attr.attnum;
	    """

    cur.execute(metadata_query, (allowed_tables, excluded_tables, excluded_tables))
    rows = cur.fetchall()

    schema_md = "# Tulip 2.0 Database Structural Schema Layout\n\n"
    current_table = ""

    for row in rows:
        table, col, dtype, is_pk, ref_table = row
        if table != current_table:
            current_table = table
            schema_md += f"\n## Table: {current_table}\n"
            schema_md += "| Column Name | Data Type | Key Mapping | References Table |\n|---|---|---|---|\n"
        
        key_type = "PK" if is_pk else ("FK" if ref_table else "")
        ref_str = ref_table if ref_table else "None"
        schema_md += f"| {col} | {dtype} | {key_type} | {ref_str} |\n"

    with open(SCHEMA_FILE, "w") as f:
        f.write(schema_md)

    print(f"✅ System map saved locally into '{SCHEMA_FILE}'")
    cur.close()
    conn.close()

if __name__ == "__main__":
    extract_database_schema()
