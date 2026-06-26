from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
from db import refresh_schema, schema_to_text

load_dotenv()

model = Groq(id="llama-3.3-70b-versatile")

_cached_schema = None
_cached_schema_text = None


def get_schema_text():
    global _cached_schema, _cached_schema_text

    new_schema = refresh_schema()

    if new_schema != _cached_schema:
        _cached_schema = new_schema
        _cached_schema_text = schema_to_text(new_schema)

    return _cached_schema_text


intent_agent = Agent(
    name="Intent Agent",
    model=model,
    instructions="""
Classify user request into ONE category.

Priority rules (IMPORTANT):
1. If text contains "procedure" or "stored procedure" => PROCEDURE
2. If text contains "function" => FUNCTION
3. If text contains "trigger" => TRIGGER
4. If text contains "view" => VIEW
5. If text contains "index" => INDEX
6. If text contains CREATE/ALTER/DROP only for tables/constraints => DDL
7. SELECT/data retrieval => QUERY
8. INSERT/UPDATE/DELETE => CRUD
9. SQL errors => DEBUG
10. Non SQL => GENERAL

Return ONLY category name.
"""
)

general_agent = Agent(
    name="General Assistant",
    model=model,
    instructions="""
You are a helpful assistant.
Give clear and concise answers.
"""
)


def get_query_agent():
    db_schema = get_schema_text()

    return Agent(
        name="Query Generator",
        model=model,
        instructions=f"""
Database Schema:
{db_schema}

Generate ONLY PostgreSQL SELECT queries.

Rules:
- Use valid schema only
- Return SQL only
"""
    )


def get_crud_agent():
    db_schema = get_schema_text()

    return Agent(
        name="CRUD Agent",
        model=model,
        instructions=f"""
Database Schema:
{db_schema}

Generate INSERT / UPDATE / DELETE queries.

Return ONLY SQL.
"""
    )


ddl_agent = Agent(
    name="DDL Agent",
    model=model,
    instructions="""
Generate PostgreSQL DDL queries.
Return ONLY SQL.
"""
)

view_agent = Agent(
    name="View Agent",
    model=model,
    instructions="""
Generate PostgreSQL VIEW queries.
Return ONLY SQL.
"""
)

procedure_agent = Agent(
    name="Procedure Agent",
    model=model,
    instructions="""
Generate PostgreSQL procedures.
Return ONLY SQL.
"""
)

function_agent = Agent(
    name="Function Agent",
    model=model,
    instructions="""
Generate PostgreSQL functions.
Return ONLY SQL.
"""
)

trigger_agent = Agent(
    name="Trigger Agent",
    model=model,
    instructions="""
Generate PostgreSQL triggers.
Return ONLY SQL.
"""
)

index_agent = Agent(
    name="Index Agent",
    model=model,
    instructions="""
Generate PostgreSQL indexes.
Return ONLY SQL.
"""
)

transaction_agent = Agent(
    name="Transaction Agent",
    model=model,
    instructions="""
Generate PostgreSQL transaction queries.
Return ONLY SQL.
"""
)

debug_agent = Agent(
    name="Debug Agent",
    model=model,
    instructions="""
Explain SQL errors.
Give:
1. Error reason
2. Fix
"""
)
validator_agent = Agent(
    name="Validator Agent",
    model=model,
    instructions="""
Validate PostgreSQL SQL query.

Rules:
1. Check syntax
2. Check schema compatibility
3. Check SQL correctness

If query is valid:
Return ONLY:
VALID

If query is invalid:
Return corrected SQL query only.
"""
)

security_agent = Agent(
    name="Security Agent",
    model=model,
    instructions="""
Check if SQL is safe.

Unsafe:
- DROP DATABASE
- mass DELETE without WHERE
- dangerous TRUNCATE

Return:
SAFE
or
UNSAFE
"""
)

explanation_agent = Agent(
    name="Explanation Agent",
    model=model,
    instructions="""
Explain SQL query in simple English.
"""
)

optimization_agent = Agent(
    name="Optimization Agent",
    model=model,
    instructions="""
Suggest SQL performance improvements.
Mention:
- indexes
- joins
- optimization tips
"""
)