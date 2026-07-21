import psycopg2
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_connection():
    return psycopg2.connect(
        host="localhost",  
        database="employees",
        user="postgres",
        password="123456"
    )


# ---------------------------
# EXECUTE SQL
# ---------------------------
def execute_query(query):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(query)

        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            df = pd.DataFrame(rows, columns=columns)

            return df, None
        else:
            conn.commit()
            return "Query executed successfully", None

    except Exception as e:
        conn.rollback()
        return None, str(e)

    finally:
        cur.close()
        conn.close()


# ---------------------------
# GET TABLE LIST
# ---------------------------
def get_tables():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = [row[0] for row in cur.fetchall()]
        return tables

    finally:
        cur.close()
        conn.close()


# ---------------------------
# REFRESH SCHEMA
# ---------------------------
def refresh_schema():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)

        rows = cur.fetchall()
        schema = {}

        for table, column, datatype in rows:
            if table not in schema:
                schema[table] = []

            schema[table].append(
                f"{column} ({datatype})"
            )

        return schema

    finally:
        cur.close()
        conn.close()


# ---------------------------
# SCHEMA TO TEXT
# ---------------------------
def schema_to_text(schema):
    schema_text = ""

    for table, columns in schema.items():
        schema_text += f"Table: {table}\n"
        schema_text += "Columns:\n"

        for col in columns:
            schema_text += f"- {col}\n"

        schema_text += "\n"

    return schema_text
